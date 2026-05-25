# placement-portal-application-v2
A full-stack web application for managing campus placements. Students can apply for job drives, companies can post vacancies and manage applications, and admins oversee the entire process.

## Setup Instructions

### Terminal 1 — Backend:
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Terminal 2 — Frontend:
```bash
cd frontendf
echo "VITE_API_URL=http://localhost:5000" > .env
npm install
npm run serve
```

### Terminal 3 — Redis + Celery:
```bash
cd backend
wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make
src/redis-server &
cd ..
celery -A app.celery worker --loglevel=info
```

The backend runs on http://localhost:5000
The frontend runs on http://localhost:8081

## Tech Stack
### Backend:
- Python, Flask
- Flask-Security (authentication & role-based access)
- Flask-SQLAlchemy + SQLite
- Celery + Redis (background tasks)
- Flask-Mail (email notifications)
- Flask-Caching

### Frontend:
- Vue.js 3
- Vue Router

## Features
### Student:
- Register and manage profile (CGPA, branch, skills, experience)
- Upload resume via profile update
- Browse and apply for placement drives
- Track application status (Applied → Shortlisted → Interview → Offer → Placed/Rejected)
- View interview schedule (date, time, venue)

### Company:
- Register and wait for admin approval before posting drives
- Create placement drives with detailed job info
- View and manage applications for each drive
- Move students through placement stages
- Schedule interview timings for shortlisted students

### Admin:
- Approve or reject company registrations
- Approve or reject placement drives
- Blacklist students or companies
- View all applications and placements
- Search across students and companies
- Export reports as CSV
- Monthly placement summary reports via email

## Application Status Flow
Applied → Shortlisted → Interview → Offer → Placed/Rejected

## Database
SQLite database stored at backend/instance/placement.db. Automatically created on first run.
