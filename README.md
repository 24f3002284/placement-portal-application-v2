# placement-portal-application-v2
A full-stack web application for managing campus placements. Students can apply for job drives, companies can post vacancies and manage applications, and admins oversee the entire process.

Instructions:
  1) Please run 'cd backend 
  pip install -r requirements.txt 
  python app.py' in one terminal.

  2) Please run 'cd frontend 
  npm install 
  npm run serve' in the second terminal.

  3) Please run 'sudo apt-get install redis-server -y 
  redis-server & 
  cd backend 
  celery -A celery_config worker --loglevel=info' 
  in the third and final terminal.

  
Tech Stack:
Backend:
  Python, Flask
  Flask-Security (authentication & role-based access)
  Flask-SQLAlchemy + SQLite
  Celery + Redis (background tasks)
  Flask-Mail (email notifications)
  Flask-Caching

Frontend:
  Vue.js 3
  Vue Router

Features:
Student:
  Register and manage profile (CGPA, branch, skills, experience)
  Upload resume via profile update
  Browse and apply for placement drives
  Track application status (Applied → Shortlisted → Interview → Offer → Placed / Rejected)
  View interview schedule (date, time, venue)

Company:
  Register and wait for admin approval before posting drives
  Create placement drives with detailed job info (package, eligible branches, min CGPA, skills required)
  View and manage applications for each drive
  Move students through placement stages
  Schedule interview timings for shortlisted students

Admin:
  Approve or reject company registrations
  Approve or reject placement drives
  Blacklist students or companies
  View all applications and placements
  Search across students and companies
  Export reports as CSV
  Monthly placement summary reports via email

Roles:
  Role        Capabilities
  Admin       Full control — approve, reject, blacklist, view all data
  Company     Post drives, manage applicants, schedule interviews
  Student     Browse drives, apply, track status


Application Status Flow: Applied -> Shortlisted -> Interview -> Offer -> Placed or Rejected

Installation & Setup:
Prerequisites:
  Python 3.10+
  Node.js
  Redis (for Celery)

Backend(bash):
  cd backend
  pip install -r requirements.txt
  python app.py

Frontend(bash):
  cd frontend
  npm install
  npm run serve
Celery Worker (for background tasks)(bash):
  cd backend
  celery -A celery_config worker --loglevel=info
  
The backend runs on http://localhost:5000 and the frontend on http://localhost:8080

Database:
SQLite database stored at backend/instance/placement.db. Automatically created on first run.
