import os, csv, io
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(32)
basedir = os.path.abspath(os.path.dirname(__file__))

# --- CONFIGURATION ---
# Ensure instance folder exists for SQLite (critical for Render/Cloud)
instance_path = os.path.join(basedir, 'instance')
os.makedirs(instance_path, exist_ok=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_path, "muranga_services.db")}'
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB Max Upload

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# --- DATABASE INITIALIZATION (MOVED OUTSIDE __MAIN__) ---
# This ensures tables are created whether running locally or on Render/Gunicorn
with app.app_context():
    db.create_all()
    print("✅ Database tables initialized successfully")

# --- HELPER FUNCTIONS ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_user():
    if 'user_id' not in session: 
        return None
    return db.session.get(User, session['user_id'])

@app.context_processor
def inject_user():
    return dict(current_user=get_current_user())

# --- STATIC FILE SERVING ---
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- DATABASE MODELS ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='citizen')
    phone = db.Column(db.String(20))
    requests = db.relationship('ServiceRequest', backref='user', lazy=True)

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300))
    status = db.Column(db.String(20), default='Pending')
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- AUTH ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        existing = User.query.filter_by(email=request.form['email']).first()
        if existing:
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))
        
        u = User(
            name=request.form['name'], 
            email=request.form['email'], 
            password=generate_password_hash(request.form['password']),
            role=request.form.get('role', 'citizen'),
            phone=request.form.get('phone', '')
        )
        db.session.add(u)
        db.session.commit()
        session['user_id'] = u.id
        flash('Welcome! Account created successfully.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(email=request.form['email']).first()
        if u and check_password_hash(u.password, request.form['password']):
            session['user_id'] = u.id
            flash(f'Welcome back, {u.name}!', 'success')
            target = 'admin_dashboard' if u.role == 'admin' else 'dashboard'
            return redirect(url_for(target))
        flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# --- CITIZEN ROUTES ---
@app.route('/dashboard')
def dashboard():
    u = get_current_user()
    if not u: 
        return redirect(url_for('login'))
    if u.role == 'admin': 
        return redirect(url_for('admin_dashboard'))
    
    reqs = ServiceRequest.query.filter_by(user_id=u.id).order_by(ServiceRequest.created_at.desc()).all()
    return render_template('dashboard.html', requests=reqs)

@app.route('/submit', methods=['GET','POST'])
def submit():
    u = get_current_user()
    if not u: 
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        img_path = None
        f = request.files.get('image')
        
        # ✅ VALIDATION INSIDE THE ROUTE
        if f and f.filename:
            if not allowed_file(f.filename):
                flash('Invalid file type. Only PNG, JPG, JPEG allowed.', 'error')
                return redirect(url_for('submit'))
                
            fn = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], fn))
            img_path = f"uploads/{fn}"
        
        r = ServiceRequest(
            user_id=u.id, 
            category=request.form['category'],
            location=request.form['location'], 
            description=request.form['description'],
            image_url=img_path
        )
        db.session.add(r)
        db.session.commit()
        flash('Request submitted successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('submit.html')

@app.route('/request/<int:req_id>')
def view_request(req_id):
    u = get_current_user()
    r = db.session.get(ServiceRequest, req_id)
    if not r:
        flash('Request not found.', 'error')
        return redirect(url_for('dashboard'))
    
    if r.user_id != u.id and (not u or u.role != 'admin'): 
        flash('Unauthorized access.', 'error')
        return redirect(url_for('dashboard'))
    return render_template('request_detail.html', req=r)

@app.route('/profile', methods=['GET','POST'])
def profile():
    u = get_current_user()
    if not u: 
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        new_name = request.form['name'].strip()
        if not new_name:
            flash('Name cannot be empty.', 'error')
            return redirect(url_for('profile'))
            
        u.name = new_name
        u.phone = request.form.get('phone', '').strip()
        
        new_pw = request.form.get('new_password', '').strip()
        if new_pw:
            if len(new_pw) < 6:
                flash('Password must be at least 6 characters.', 'error')
                return redirect(url_for('profile'))
            u.password = generate_password_hash(new_pw)
            
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
        
    return render_template('profile.html', user=u)

# --- ADMIN ROUTES ---
@app.route('/admin')
def admin_dashboard():
    u = get_current_user()
    if not u or u.role != 'admin': 
        return redirect(url_for('dashboard'))
    
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    
    query = ServiceRequest.query.order_by(ServiceRequest.created_at.desc())
    if search:
        query = query.filter(
            (ServiceRequest.description.ilike(f'%{search}%')) | 
            (ServiceRequest.location.ilike(f'%{search}%'))
        )
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    reqs = query.all()
    stats = {
        'pending': ServiceRequest.query.filter_by(status='Pending').count(),
        'in_progress': ServiceRequest.query.filter_by(status='In Progress').count(),
        'resolved': ServiceRequest.query.filter_by(status='Resolved').count(),
        'total': ServiceRequest.query.count()
    }
    return render_template('admin.html', requests=reqs, stats=stats, 
                          search=search, status_filter=status_filter)

@app.route('/admin/update-status/<int:req_id>', methods=['POST'])
def update_status(req_id):
    r = db.session.get(ServiceRequest, req_id)
    if not r:
        flash('Request not found.', 'error')
        return redirect(url_for('admin_dashboard'))
    
    r.status = request.form['status']
    r.admin_notes = request.form.get('admin_notes', '').strip()
    db.session.commit()
    flash(f'Request #{req_id} updated to {r.status}', 'success')
    
    return redirect(url_for('admin_dashboard', 
                           search=request.args.get('search', ''), 
                           status_filter=request.args.get('status', '')))

@app.route('/admin/export-csv')
def export_csv():
    u = get_current_user()
    if not u or u.role != 'admin': 
        return redirect(url_for('dashboard'))
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Citizen Name', 'Category', 'Location', 'Status', 'Date Submitted', 'Description'])
    
    for r in ServiceRequest.query.order_by(ServiceRequest.created_at.desc()).all():
        writer.writerow([
            r.id, r.user.name, r.category, r.location, r.status,
            r.created_at.strftime('%Y-%m-%d %H:%M'), r.description
        ])
    
    output.seek(0)
    filename = f'muranga_requests_{datetime.now().strftime("%Y%m%d_%H%M")}.csv'
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

# --- LOCAL DEVELOPMENT ONLY ---
if __name__ == '__main__':
    print("\n Starting Murang'a Service Portal on http://127.0.0.1:8000")
    app.run(debug=True, port=8000)