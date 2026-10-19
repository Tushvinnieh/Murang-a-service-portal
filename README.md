# Murang'a County Service Portal

A Flask-based web application for managing citizen service requests. Built as part of the Murang'a County ICT Internship program to digitize infrastructure reporting and administrative workflows.

**Tech Stack**
1. Backend: Python 3.10+, Flask 3.0, SQLAlchemy ORM
2. Frontend: HTML5, CSS3, Vanilla JavaScript, Jinja2 Templating
3. Database: SQLite (dev), PostgreSQL-ready schema
4. Deployment: Gunicorn WSGI server, Render.com

**Core Features**
1. Role-based access control: Separate dashboards for citizens and county admins
2. Secure file uploads: 16MB limit with extension validation (PNG/JPG/JPEG only)
3. Real-time status tracking: Visual timeline showing request progression (Pending → In Progress → Resolved)
4. Admin analytics: CSV export with UTF-8-BOM encoding for Excel compatibility
5. Responsive design: Mobile-first layout with collapsible sidebar navigation
6. Profile management: Secure user updates with password change validation

## Local Setup

1. **Clone and navigate:**
   ```bash
   git clone https://github.com/Tushvinnieh/Murang-a-service-portal.git
   cd Murang-a-service-portal
   python -m venv venv

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate


3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt

3. **Run Locally:**
   ```bash
   python app.py

Access at http://127.0.0.1:8000

## Security Implementation
1. Passwords hashed using PBKDF2-SHA256 via Werkzeug
2. SQL injection prevented through SQLAlchemy parameterized queries
3. XSS protection via Jinja2 auto-escaping
4. Session signing with cryptographically random secret key
5.File upload validation prevents malicious script execution

## Known Limitations & Future Work
1. Image persistence: Free-tier Render deletes uploads on redeploy. Production fix: integrate Cloudinary/S3.
2. SMS notifications: Planned integration with Africa's Talking API for real-time status alerts.
3. GIS mapping: Next phase will add Leaflet.js to visualize infrastructure hotspots by ward.
4. Multi-language support: Swahili/Kikuyu toggle for rural accessibility.


## Author
Vincent Mwenda Mutuma (Tushvinnieh)
ICT Internship Candidate - Murang'a County Government

