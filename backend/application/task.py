from celery import shared_task
from time import sleep
import os

@shared_task(name="add_together", ignore_result=False)
def add_together(a, b):
    sleep(10)
    return a + b


from .models import db, StudentProfile, CompanyProfile, PlacementDrive, Application, Placement
import csv
import requests
from datetime import datetime, date, timedelta


def get_static_dir():
    """Get or create static directory for CSV exports"""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    os.makedirs(static_dir, exist_ok=True)
    return static_dir

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

    with open(f"./static/{csv_filename}", "w") as file:
        writer = csv.writer(file,delimiter=",")
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

    return f"./static/{csv_filename}"

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
        writer = csv.writer(file)
        writer.writerow(["Sr No.", "Drive Title", "Student Name", "Student Email",
                         "Branch", "CGPA", "Application Status", "Applied Date",
                         "Interview Date", "Notes"])
        row_num = 1
        for drive in drives:
            for app in drive.applications:
                student = StudentProfile.query.filter_by(user_id=app.student_id).first()
                writer.writerow([
                    row_num, drive.job_title,
                    student.name if student else "N/A",
                    student.email if student else "N/A",
                    student.branch if student else "",
                    student.cgpa if student else "",
                    app.status,
                    app.applied_at.strftime("%Y-%m-%d") if app.applied_at else "",
                    app.interview_date.strftime("%Y-%m-%d") if app.interview_date else "",
                    app.notes or ""
                ])
                row_num += 1

    return filepath


# ─── Interview Reminder Job (Daily) ───────────────────────────────────────────
@shared_task(name="application.task.send_interview_reminders")
def send_interview_reminders():
    from flask import current_app
    tomorrow = date.today() + timedelta(days=1)
    interviews = Application.query.filter(
        Application.interview_date == tomorrow,
        Application.status == "Interview"
    ).all()

    if not interviews:
        return "No interviews scheduled for tomorrow"

    webhook_url = "https://chat.googleapis.com/v1/spaces/AAQAeNAnOpw/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=MqIDBOvWJsrYuc-7722lxc8mLoSZ9nP4dGfB-laBEbY"
    mail_username = current_app.config.get("MAIL_USERNAME", "")

    for app_rec in interviews:
        student = StudentProfile.query.filter_by(user_id=app_rec.student_id).first()
        drive = PlacementDrive.query.get(app_rec.drive_id)
        company = CompanyProfile.query.filter_by(user_id=drive.company_id).first() if drive else None
        if not student or not drive:
            continue

        msg = (
            f"Hi {student.name}! Reminder: You have an interview TOMORROW "
            f"for {drive.job_title} at {company.name if company else 'N/A'}. "
            f"Time: {app_rec.interview_time or 'TBD'}, "
            f"Venue: {app_rec.interview_venue or 'TBD'}. Good luck!"
        )

        if webhook_url:
            try:
                requests.post(webhook_url, json={"text": msg}, timeout=5)
            except Exception as e:
                print(f"GChat error: {e}")

        if mail_username:
            try:
                from flask_mail import Mail, Message
                mail = Mail(current_app)
                mail.send(Message(
                    subject=f"Interview Reminder – {drive.job_title}",
                    recipients=[student.email], body=msg
                ))
            except Exception as e:
                print(f"Email error: {e}")

    return f"Reminders sent for {len(interviews)} interviews"


# ─── Deadline Reminder Job (Daily) ────────────────────────────────────────────
@shared_task(name="application.task.send_deadline_reminders")
def send_deadline_reminders():
    """Send reminders to eligible students whose application deadline is tomorrow."""
    from flask import current_app
    tomorrow = date.today() + timedelta(days=1)

    drives = PlacementDrive.query.filter(
        PlacementDrive.application_deadline == tomorrow,
        PlacementDrive.status == "Approved"
    ).all()

    if not drives:
        return "No application deadlines tomorrow"

    webhook_url = current_app.config.get("GCHAT_WEBHOOK_URL", "")
    mail_username = current_app.config.get("MAIL_USERNAME", "")
    reminded = 0

    for drive in drives:
        company = CompanyProfile.query.filter_by(user_id=drive.company_id).first()
        applied_ids = {a.student_id for a in Application.query.filter_by(drive_id=drive.id).all()}
        students = StudentProfile.query.filter_by(status="Active").all()
        eligible_unapplied = [s for s in students if s.user_id not in applied_ids]

        for student in eligible_unapplied:
            msg = (
                f"Hi {student.name}! Deadline Reminder: The application for "
                f"{drive.job_title} at {company.name if company else 'N/A'} "
                f"closes TOMORROW ({tomorrow.strftime('%d %b %Y')}). "
                f"Package: {drive.package or 'N/A'}. Don't miss it!"
            )

            if webhook_url:
                try:
                    requests.post(webhook_url, json={"text": msg}, timeout=5)
                except Exception as e:
                    print(f"GChat error: {e}")

            if mail_username and student.email:
                try:
                    from flask_mail import Mail, Message
                    Mail(current_app).send(Message(
                        subject=f"Deadline Tomorrow – {drive.job_title}",
                        recipients=[student.email],
                        body=msg
                    ))
                except Exception as e:
                    print(f"Email error: {e}")

            reminded += 1

    return f"Deadline reminders sent to {reminded} students across {len(drives)} drives"


# ─── Monthly Report ───────────────────────────────────────────────────────────
@shared_task(name="application.task.send_monthly_report")
def send_monthly_report():
    from flask import current_app
    today = date.today()
    month_label = (today.replace(day=1) - timedelta(days=1)).strftime("%B %Y")
    mail_username = current_app.config.get("MAIL_USERNAME", "")
    admin_email = current_app.config.get("ADMIN_EMAIL", "")

    companies = CompanyProfile.query.filter_by(status="Approved").all()
    for company in companies:
        drives = PlacementDrive.query.filter_by(company_id=company.user_id).all()
        total_apps = sum(len(d.applications) for d in drives)
        placed = sum(len([a for a in d.applications if a.status == "Placed"]) for d in drives)

        drive_rows = "".join([
            f"<tr><td>{d.job_title}</td><td>{d.status}</td><td>{len(d.applications)}</td>"
            f"<td>{len([a for a in d.applications if a.status=='Placed'])}</td></tr>"
            for d in drives
        ])

        html = f"""<html><body style="font-family:Arial,sans-serif;padding:20px;">
        <h2>Monthly Placement Report – {month_label}</h2>
        <h3>{company.name}</h3>
        <table border="1" cellpadding="8" style="border-collapse:collapse;margin-bottom:20px;">
            <tr style="background:#1a237e;color:white;"><th>Metric</th><th>Count</th></tr>
            <tr><td>Total Drives</td><td>{len(drives)}</td></tr>
            <tr><td>Total Applications</td><td>{total_apps}</td></tr>
            <tr><td>Students Placed</td><td>{placed}</td></tr>
        </table>
        <table border="1" cellpadding="8" style="border-collapse:collapse;">
            <tr style="background:#1a237e;color:white;"><th>Job Title</th><th>Status</th><th>Applicants</th><th>Placed</th></tr>
            {drive_rows}
        </table></body></html>"""

        if mail_username and company.email:
            try:
                from flask_mail import Mail, Message
                Mail(current_app).send(Message(
                    subject=f"Monthly Placement Report – {month_label}",
                    recipients=[company.email], html=html
                ))
            except Exception as e:
                print(f"Email error ({company.email}): {e}")

    # Admin summary
    if mail_username and admin_email:
        try:
            from flask_mail import Mail, Message
            admin_html = f"""<html><body style="font-family:Arial,sans-serif;padding:20px;">
            <h2>System Report – {month_label}</h2>
            <table border="1" cellpadding="8" style="border-collapse:collapse;">
                <tr style="background:#1a237e;color:white;"><th>Metric</th><th>Total</th></tr>
                <tr><td>Students</td><td>{StudentProfile.query.count()}</td></tr>
                <tr><td>Active Companies</td><td>{len(companies)}</td></tr>
                <tr><td>Total Drives</td><td>{PlacementDrive.query.count()}</td></tr>
                <tr><td>Total Applications</td><td>{Application.query.count()}</td></tr>
                <tr><td>Total Placed</td><td>{Application.query.filter_by(status="Placed").count()}</td></tr>
            </table></body></html>"""
            Mail(current_app).send(Message(
                subject=f"Admin System Report – {month_label}",
                recipients=[admin_email], html=admin_html
            ))
        except Exception as e:
            print(f"Admin email error: {e}")

    return f"Monthly reports sent to {len(companies)} companies + admin"


# ─── Student PDF Export ───────────────────────────────────────────────────────
@shared_task(name="student_pdf", ignore_result=False)
def student_pdf(student_id):
    from weasyprint import HTML
    student = StudentProfile.query.filter_by(user_id=student_id).first()
    if not student:
        return "Student not found"

    applications = Application.query.filter_by(student_id=student_id).all()

    rows = ""
    for i, app in enumerate(applications):
        drive = PlacementDrive.query.get(app.drive_id)
        company = CompanyProfile.query.filter_by(user_id=drive.company_id).first() if drive else None
        status_color = {
            "Applied": "#3b82f6", "Shortlisted": "#8b5cf6",
            "Interview": "#f59e0b", "Offer": "#10b981",
            "Placed": "#059669", "Rejected": "#ef4444"
        }.get(app.status, "#6b7280")
        rows += f"""
        <tr>
            <td>{i+1}</td>
            <td>{student.roll_number or student_id}</td>
            <td>{company.name if company else 'N/A'}</td>
            <td>{drive.job_title if drive else 'N/A'}</td>
            <td>{drive.package if drive else 'N/A'}</td>
            <td><span style="background:{status_color};color:white;padding:2px 8px;border-radius:4px;font-size:12px">{app.status}</span></td>
            <td>{app.applied_at.strftime('%Y-%m-%d') if app.applied_at else ''}</td>
            <td>{app.interview_date.strftime('%Y-%m-%d') if app.interview_date else '-'}</td>
            <td>{app.interview_time or '-'}</td>
            <td>{app.interview_venue or '-'}</td>
        </tr>"""

    placed_count = sum(1 for a in applications if a.status == "Placed")
    interview_count = sum(1 for a in applications if a.status == "Interview")

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; padding: 30px; color: #1f2937; }}
  h1 {{ color: #1e3a8a; border-bottom: 3px solid #1e3a8a; padding-bottom: 10px; }}
  .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 20px 0; background: #f8fafc; padding: 15px; border-radius: 8px; }}
  .info-item {{ font-size: 13px; }} .info-item strong {{ color: #374151; }}
  .stats {{ display: flex; gap: 15px; margin: 20px 0; }}
  .stat-box {{ flex: 1; text-align: center; padding: 15px; border-radius: 8px; color: white; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 12px; }}
  th {{ background: #1e3a8a; color: white; padding: 10px 8px; text-align: left; }}
  td {{ padding: 8px; border-bottom: 1px solid #e5e7eb; }}
  tr:nth-child(even) {{ background: #f9fafb; }}
  .footer {{ margin-top: 30px; font-size: 11px; color: #9ca3af; text-align: center; }}
</style>
</head>
<body>
  <h1>📋 My Applications Report</h1>
  <div class="info-grid">
    <div class="info-item"><strong>Name:</strong> {student.name}</div>
    <div class="info-item"><strong>Email:</strong> {student.email}</div>
    <div class="info-item"><strong>Roll Number:</strong> {student.roll_number or 'N/A'}</div>
    <div class="info-item"><strong>Branch:</strong> {student.branch or 'N/A'}</div>
    <div class="info-item"><strong>CGPA:</strong> {student.cgpa or 'N/A'}</div>
    <div class="info-item"><strong>Year:</strong> {student.year or 'N/A'}</div>
  </div>
  <div class="stats">
    <div class="stat-box" style="background:#3b82f6"><div style="font-size:24px;font-weight:bold">{len(applications)}</div><div>Total Applied</div></div>
    <div class="stat-box" style="background:#f59e0b"><div style="font-size:24px;font-weight:bold">{interview_count}</div><div>Interviews</div></div>
    <div class="stat-box" style="background:#059669"><div style="font-size:24px;font-weight:bold">{placed_count}</div><div>Placed</div></div>
  </div>
  <table>
    <thead><tr>
      <th>#</th><th>Roll No.</th><th>Company</th><th>Job Title</th>
      <th>Package</th><th>Status</th><th>Applied</th>
      <th>Interview Date</th><th>Time</th><th>Venue</th>
    </tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <div class="footer">Generated on {date.today().strftime('%d %B %Y')} · Placement Portal</div>
</body>
</html>"""

    static_dir = get_static_dir()
    pdf_filename = f"student-{student_id}.pdf"
    filepath = os.path.join(static_dir, pdf_filename)
    HTML(string=html_content).write_pdf(filepath)
    return filepath


# ─── Company PDF Export ───────────────────────────────────────────────────────
@shared_task(name="company_pdf", ignore_result=False)
def company_pdf(company_id):
    from weasyprint import HTML
    company = CompanyProfile.query.filter_by(user_id=company_id).first()
    if not company:
        return "Company not found"

    drives = PlacementDrive.query.filter_by(company_id=company_id).all()
    total_apps = sum(len(d.applications) for d in drives)
    total_placed = sum(len([a for a in d.applications if a.status == "Placed"]) for d in drives)
    total_interviews = sum(len([a for a in d.applications if a.status == "Interview"]) for d in drives)

    drives_html = ""
    for drive in drives:
        rows = ""
        for app in drive.applications:
            student = StudentProfile.query.filter_by(user_id=app.student_id).first()
            status_color = {
                "Applied": "#3b82f6", "Shortlisted": "#8b5cf6",
                "Interview": "#f59e0b", "Offer": "#10b981",
                "Placed": "#059669", "Rejected": "#ef4444"
            }.get(app.status, "#6b7280")
            rows += f"""
            <tr>
                <td>{student.name if student else 'N/A'}</td>
                <td>{student.email if student else 'N/A'}</td>
                <td>{student.branch if student else ''}</td>
                <td>{student.cgpa if student else ''}</td>
                <td><span style="background:{status_color};color:white;padding:2px 8px;border-radius:4px;font-size:11px">{app.status}</span></td>
                <td>{app.applied_at.strftime('%Y-%m-%d') if app.applied_at else ''}</td>
                <td>{app.interview_date.strftime('%Y-%m-%d') if app.interview_date else '-'}</td>
                <td>{app.notes or '-'}</td>
            </tr>"""

        if drive.applications:
            drives_html += f"""
            <div style="margin-top:25px">
              <h3 style="color:#1e3a8a;margin-bottom:5px">{drive.job_title}
                <span style="font-size:12px;font-weight:normal;color:#6b7280">· {drive.package or 'N/A'} · {len(drive.applications)} applicants</span>
              </h3>
              <table width="100%" style="border-collapse:collapse;font-size:11px">
                <thead><tr style="background:#1e3a8a;color:white">
                  <th style="padding:8px">Name</th><th style="padding:8px">Email</th>
                  <th style="padding:8px">Branch</th><th style="padding:8px">CGPA</th>
                  <th style="padding:8px">Status</th><th style="padding:8px">Applied</th>
                  <th style="padding:8px">Interview</th><th style="padding:8px">Notes</th>
                </tr></thead>
                <tbody>{rows}</tbody>
              </table>
            </div>"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; padding: 30px; color: #1f2937; }}
  h1 {{ color: #1e3a8a; border-bottom: 3px solid #1e3a8a; padding-bottom: 10px; }}
  .stats {{ display: flex; gap: 15px; margin: 20px 0; }}
  .stat-box {{ flex: 1; text-align: center; padding: 15px; border-radius: 8px; color: white; }}
  td {{ padding: 7px 8px; border-bottom: 1px solid #e5e7eb; }}
  tr:nth-child(even) {{ background: #f9fafb; }}
  .footer {{ margin-top: 30px; font-size: 11px; color: #9ca3af; text-align: center; }}
</style>
</head>
<body>
  <h1>🏢 Company Placement Report</h1>
  <p style="color:#6b7280">{company.name} · {company.industry or ''} · {company.location or ''}</p>
  <div class="stats">
    <div class="stat-box" style="background:#3b82f6"><div style="font-size:24px;font-weight:bold">{len(drives)}</div><div>Total Drives</div></div>
    <div class="stat-box" style="background:#3b82f6"><div style="font-size:24px;font-weight:bold">{total_apps}</div><div>Total Applications</div></div>
    <div class="stat-box" style="background:#f59e0b"><div style="font-size:24px;font-weight:bold">{total_interviews}</div><div>Interviews</div></div>
    <div class="stat-box" style="background:#059669"><div style="font-size:24px;font-weight:bold">{total_placed}</div><div>Placed</div></div>
  </div>
  {drives_html}
  <div class="footer">Generated on {date.today().strftime('%d %B %Y')} · Placement Portal</div>
</body>
</html>"""

    static_dir = get_static_dir()
    pdf_filename = f"company-{company_id}.pdf"
    filepath = os.path.join(static_dir, pdf_filename)
    HTML(string=html_content).write_pdf(filepath)
    return filepath