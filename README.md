# Murang'a County Service Portal

A Flask-based web application for managing citizen service requests. Built as part of the Murang'a County ICT Internship program to digitize infrastructure reporting and administrative workflows.

**Tech Stack**
Backend: Python 3.10+, Flask 3.0, SQLAlchemy ORM
Frontend: HTML5, CSS3, Vanilla JavaScript, Jinja2 Templating
Database: SQLite (dev), PostgreSQL-ready schema
Deployment: Gunicorn WSGI server, Render.com

**Core Features**
Role-based access control: Separate dashboards for citizens and county admins
Secure file uploads: 16MB limit with extension validation (PNG/JPG/JPEG only)
Real-time status tracking: Visual timeline showing request progression (Pending → In Progress → Resolved)
Admin analytics: CSV export with UTF-8-BOM encoding for Excel compatibility
Responsive design: Mobile-first layout with collapsible sidebar navigation
Profile management: Secure user updates with password change validation

## Local Setup

1. **Clone and navigate:**
   ```bash
   git clone https://github.com/Tushvinnieh/Murang-a-service-portal.git
   cd Murang-a-service-portal
   python -m venv venv

2.** Create virtual environment  ** 
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

3.**Install dependancies**
pip install -r requirements.txt 

4.**Run Locally**
python app.py

Access at http://127.0.0.1:8000

## Security Implementation
Passwords hashed using PBKDF2-SHA256 via Werkzeug
SQL injection prevented through SQLAlchemy parameterized queries
XSS protection via Jinja2 auto-escaping
Session signing with cryptographically random secret key
File upload validation prevents malicious script execution

## Known Limitations & Future Work
Image persistence: Free-tier Render deletes uploads on redeploy. Production fix: integrate Cloudinary/S3.
SMS notifications: Planned integration with Africa's Talking API for real-time status alerts.
GIS mapping: Next phase will add Leaflet.js to visualize infrastructure hotspots by ward.
Multi-language support: Swahili/Kikuyu toggle for rural accessibility.

## Author
Vincent Mwenda Mutuma (Tushvinnieh)
ICT Internship Candidate - Murang'a County Government

