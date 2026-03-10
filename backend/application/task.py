from celery import shared_task
from time import sleep
import os
from .mail import send_email

# ── NO "from app import celery" here – that causes a circular import ──────────

@shared_task(name="add_together", ignore_result=False)
def add_together(a, b):
    sleep(10)
    return a + b


from .models import db, StudentProfile, CompanyProfile, PlacementDrive, Application, Placement, Role
import csv
from datetime import datetime, date, timedelta


def get_static_dir():
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    os.makedirs(static_dir, exist_ok=True)
    return static_dir


# ─── Student CSV Export ───────────────────────────────────────────────────────
@shared_task(name="student_csv", ignore_result=False)
def student_csv(student_id):
    sleep(2)
    student = StudentProfile.query.filter_by(user_id=student_id).first()
    if not student:
        return "Student not found"

    applications = Application.query.filter_by(student_id=student_id).all()
    static_dir = get_static_dir()
    csv_filename = f"student-{student_id}.csv"
    filepath = os.path.join(static_dir, csv_filename)

    with open(filepath, "w", newline="") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(["Sr No.", "Roll Number", "Company", "Job Title", "Package",
                         "Status", "Applied Date", "Interview Date", "Interview Time",
                         "Interview Venue", "Notes"])
        for i, app in enumerate(applications):
            drive = PlacementDrive.query.get(app.drive_id)
            company = CompanyProfile.query.filter_by(user_id=drive.company_id).first() if drive else None
            writer.writerow([
                i + 1,
                student.roll_number or student_id,
                company.name if company else "N/A",
                drive.job_title if drive else "N/A",
                drive.package if drive else "N/A",
                app.status,
                app.applied_at.strftime("%Y-%m-%d") if app.applied_at else "",
                app.interview_date.strftime("%Y-%m-%d") if app.interview_date else "",
                app.interview_time or "",
                app.interview_venue or "",
                app.notes or ""
            ])

    return csv_filename


# ─── Company CSV Export ───────────────────────────────────────────────────────
@shared_task(name="company_csv", ignore_result=False)
def company_csv(company_id):
    sleep(2)
    company = CompanyProfile.query.filter_by(user_id=company_id).first()
    if not company:
        return "Company not found"

    drives = PlacementDrive.query.filter_by(company_id=company_id).all()
    static_dir = get_static_dir()
    csv_filename = f"company-{company_id}.csv"
    filepath = os.path.join(static_dir, csv_filename)

    with open(filepath, "w", newline="") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(["Sr No.", "Drive Title", "Student Name", "Roll Number",
                         "Branch", "CGPA", "Status", "Applied Date",
                         "Interview Date", "Interview Time", "Interview Venue", "Notes"])
        row = 1
        for drive in drives:
            for app in drive.applications:
                student = StudentProfile.query.filter_by(user_id=app.student_id).first()
                writer.writerow([
                    row,
                    drive.job_title,
                    student.name if student else "N/A",
                    student.roll_number if student else "",
                    student.branch if student else "",
                    student.cgpa if student else "",
                    app.status,
                    app.applied_at.strftime("%Y-%m-%d") if app.applied_at else "",
                    app.interview_date.strftime("%Y-%m-%d") if app.interview_date else "",
                    app.interview_time or "",
                    app.interview_venue or "",
                    app.notes or ""
                ])
                row += 1

    return csv_filename


# ─── Admin CSV Export ─────────────────────────────────────────────────────────
@shared_task(name="admin_csv", ignore_result=False)
def admin_csv():
    sleep(2)
    applications = Application.query.all()
    static_dir = get_static_dir()
    csv_filename = "admin-all-applications.csv"
    filepath = os.path.join(static_dir, csv_filename)

    with open(filepath, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Sr No.", "Student Name", "Student Email", "Roll Number",
                         "Branch", "CGPA", "Company", "Job Title", "Package",
                         "Status", "Applied Date", "Interview Date",
                         "Interview Time", "Interview Venue", "Notes"])
        for i, app in enumerate(applications):
            student = StudentProfile.query.filter_by(user_id=app.student_id).first()
            drive = PlacementDrive.query.get(app.drive_id)
            company = CompanyProfile.query.filter_by(user_id=drive.company_id).first() if drive else None
            writer.writerow([
                i + 1,
                student.name if student else "N/A",
                student.email if student else "N/A",
                student.roll_number if student else "",
                student.branch if student else "",
                student.cgpa if student else "",
                company.name if company else "N/A",
                drive.job_title if drive else "N/A",
                drive.package if drive else "N/A",
                app.status,
                app.applied_at.strftime("%Y-%m-%d") if app.applied_at else "",
                app.interview_date.strftime("%Y-%m-%d") if app.interview_date else "",
                app.interview_time or "",
                app.interview_venue or "",
                app.notes or ""
            ])

    return csv_filename


# ─── Admin Monthly Report Email ───────────────────────────────────────────────
from .utility import render_email_template

@shared_task(name="Admin_monthly_Report", ignore_result=False)
def admin_monthly_report():
    applications = db.session.query(Application).all()
    username = "Admin"
    email_content = render_email_template(
        username, applications, "./templates/admin_monthly_report.html"
    )
    send_email("admin@placement.edu", "Here is the monthly report", email_content)
    return "Email sent"


# ─── Long task (for testing) ──────────────────────────────────────────────────
@shared_task(name="long_task", bind=True, ignore_result=False)
def long_task(self, duration):
    for i in range(duration):
        sleep(1)
        self.update_state(state='PROGRESS', meta={'current': i + 1, 'total': duration})
    return {'status': 'Task completed!', 'total': duration}