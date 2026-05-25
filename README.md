# placement-portal-application-v2
A full-stack web application for managing campus placements. Students can apply for job drives, companies can post vacancies and manage applications, and admins oversee the entire process.

Instructions:
  1) Please run 'cd backend 
  pip install -r requirements.txt 
  python app.py' in one terminal.

  2) Please run 'cd frontendf 
  npm install 
  npm run serve' in the second terminal.

  3) Please run 'sudo apt-get install redis-server -y 
  redis-server & 
  cd backend 
  celery -A app.celery worker --loglevel=info' 
  in the third and final terminal.

  
Tech Stack:
Backend:
 1) Python, Flask
 2) Flask-Security (authentication & role-based access)
 3) Flask-SQLAlchemy + SQLite
 4) Celery + Redis (background tasks)
 5) Flask-Mail (email notifications)
 6) Flask-Caching

Frontend:
 1) Vue.js 3
 2) Vue Router

Features:
Student:
 1) Register and manage profile (CGPA, branch, skills, experience)
 2) Upload resume via profile update
 3) Browse and apply for placement drives
 4) Track application status (Applied → Shortlisted → Interview → Offer → Placed / Rejected)
 5) View interview schedule (date, time, venue)

Company:
 1) Register and wait for admin approval before posting drives
 2) Create placement drives with detailed job info (package, eligible branches, min CGPA, skills required)
 3) View and manage applications for each drive
 4) Move students through placement stages
 5) Schedule interview timings for shortlisted students

Admin:
 1) Approve or reject company registrations
 2) Approve or reject placement drives
 3) Blacklist students or companies
 4) View all applications and placements
 5) Search across students and companies
 6) Export reports as CSV
 7) Monthly placement summary reports via email

Roles:
 1) Role        Capabilities
 2) Admin       Full control — approve, reject, blacklist, view all data
 3) Company     Post drives, manage applicants, schedule interviews
 4) Student     Browse drives, apply, track status


Application Status Flow: Applied -> Shortlisted -> Interview -> Offer -> Placed or Rejected

Installation & Setup:
Prerequisites:
 1) Python 3.10+
 2) Node.js
 3) Redis (for Celery)

Backend(bash):
 1) cd backend
 2) pip install -r requirements.txt
 3) python app.py

Frontend(bash):
 1) cd frontendf
 2) npm install
 3) npm run serve
Celery Worker (for background tasks)(bash):
 1) cd backend
 2) celery -A celery_config worker --loglevel=info
  
The backend runs on http://localhost:5000 and the frontend on http://localhost:8080

Database:
SQLite database stored at backend/instance/placement.db. Automatically created on first run.
