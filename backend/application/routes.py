from flask import current_app as app
from flask import request,send_from_directory
from flask_security import auth_required, roles_required, current_user, hash_password
from flask_security.utils import verify_and_update_password
from .models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application, Placement
from datetime import datetime, date
from sqlalchemy import or_
import sys


def get_cache():
    from app import cache
    return cache

@app.route("/")
def home():
    return {"message": "Placement Portal API"}

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    datastore = app.security.datastore
    user = datastore.find_user(email=data.get("email"))
    if user and verify_and_update_password(data.get("password"), user):
        return {
            "token": user.get_auth_token(),
            "role": user.roles[0].name,
            "email": user.email,
            "name": user.name
        }, 200
    return {"message": "Invalid email or password"}, 401

@app.route("/register", methods=["POST"])
def register():
    role = request.args.get("role")
    data = request.json
    datastore = app.security.datastore

    if datastore.find_user(email=data.get("email")):
        return {"message": "Email already exists"}, 400

    if role == "student":
        user = datastore.create_user(
            name=data["name"], email=data["email"],
            password=hash_password(data["password"]), roles=["student"]
        )
        db.session.commit()
        db.session.add(StudentProfile(
            name=data["name"], email=data["email"],
            mobile=data.get("mobile", ""), branch=data.get("branch", ""),
            cgpa=float(data.get("cgpa", 0)), year=int(data.get("year", 1)),
            roll_number=data.get("roll_number", ""),
            skills=data.get("skills", ""), experience=data.get("experience", ""),
            user_id=user.id
        ))
        db.session.commit()
        return {"message": "Student registered successfully"}, 201

    elif role == "company":
        user = datastore.create_user(
            name=data["name"], email=data["email"],
            password=hash_password(data["password"]), roles=["company"]
        )
        db.session.commit()
        db.session.add(CompanyProfile(
            name=data["name"], email=data["email"],
            hr_contact=data.get("hr_contact", ""), website=data.get("website", ""),
            description=data.get("description", ""), industry=data.get("industry", ""),
            location=data.get("location", ""), user_id=user.id
        ))
        db.session.commit()
        return {"message": "Company registered. Awaiting admin approval."}, 201

    return {"message": "Invalid role"}, 400


# ══════════════════════════════════════════════════════════════
#  ADMIN
# ══════════════════════════════════════════════════════════════

@app.route("/api/admin-stats")
@auth_required("token")
@roles_required("admin")
def admin_stats():
    return {
        "total_students": StudentProfile.query.count(),
        "total_companies": CompanyProfile.query.count(),
        "total_drives": PlacementDrive.query.count(),
        "total_applications": Application.query.count(),
        "total_placements": Placement.query.count(),
        "pending_companies": CompanyProfile.query.filter_by(status="Registered").count(),
        "pending_drives": PlacementDrive.query.filter_by(status="Pending").count(),
    }, 200


@app.route("/api/companies")
@auth_required("token")
@roles_required("admin")
def get_companies():
    result = {"Registered": [], "Approved": [], "Rejected": [], "Blacklisted": []}
    for c in CompanyProfile.query.all():
        result[c.status].append({
            "company_id": c.id, "Company Name": c.name, "Company Email": c.email,
            "HR Contact": c.hr_contact, "Website": c.website, "Industry": c.industry,
            "Location": c.location, "Description": c.description, "Status": c.status
        })
    return result, 200


@app.route("/api/students")
@auth_required("token")
@roles_required("admin")
def get_students():
    result = {"Active": [], "Blacklisted": []}
    for s in StudentProfile.query.all():
        result[s.status].append({
            "student_id": s.id, "Student Name": s.name, "Student Email": s.email,
            "Mobile": s.mobile, "Branch": s.branch, "CGPA": s.cgpa,
            "Year": s.year, "Roll Number": s.roll_number,
            "Skills": s.skills, "Experience": s.experience, "Status": s.status
        })
    return result, 200


@app.route("/api/approve-company/<int:cid>")
@auth_required("token")
@roles_required("admin")
def approve_company(cid):
    c = CompanyProfile.query.get_or_404(cid)
    c.status = "Approved"
    db.session.commit()
    return {"message": "Company approved"}, 200


@app.route("/api/reject-company/<int:cid>")
@auth_required("token")
@roles_required("admin")
def reject_company(cid):
    c = CompanyProfile.query.get_or_404(cid)
    c.status = "Rejected"
    db.session.commit()
    return {"message": "Company rejected"}, 200


@app.route("/api/blacklist-company/<int:cid>")
@auth_required("token")
@roles_required("admin")
def blacklist_company(cid):
    c = CompanyProfile.query.get_or_404(cid)
    c.status = "Blacklisted"
    db.session.commit()
    return {"message": "Company blacklisted"}, 200


@app.route("/api/unblacklist-company/<int:cid>")
@auth_required("token")
@roles_required("admin")
def unblacklist_company(cid):
    c = CompanyProfile.query.get_or_404(cid)
    c.status = "Approved"
    db.session.commit()
    return {"message": "Company unblacklisted"}, 200


@app.route("/api/blacklist-student/<int:sid>")
@auth_required("token")
@roles_required("admin")
def blacklist_student(sid):
    s = StudentProfile.query.get_or_404(sid)
    s.status = "Blacklisted"
    db.session.commit()
    return {"message": "Student blacklisted"}, 200


@app.route("/api/unblacklist-student/<int:sid>")
@auth_required("token")
@roles_required("admin")
def unblacklist_student(sid):
    s = StudentProfile.query.get_or_404(sid)
    s.status = "Active"
    db.session.commit()
    return {"message": "Student unblacklisted"}, 200


@app.route("/api/all-drives")
@auth_required("token")
@roles_required("admin")
def get_all_drives():
    result = {"Pending": [], "Approved": [], "Rejected": [], "Closed": []}
    for d in PlacementDrive.query.all():
        company = CompanyProfile.query.filter_by(user_id=d.company_id).first()
        result[d.status].append(_drive_dict(d, company))
    return result, 200


@app.route("/api/approve-drive/<int:did>")
@auth_required("token")
@roles_required("admin")
def approve_drive(did):
    d = PlacementDrive.query.get_or_404(did)
    d.status = "Approved"
    db.session.commit()
    return {"message": "Drive approved"}, 200


@app.route("/api/reject-drive/<int:did>")
@auth_required("token")
@roles_required("admin")
def reject_drive(did):
    d = PlacementDrive.query.get_or_404(did)
    d.status = "Rejected"
    db.session.commit()
    return {"message": "Drive rejected"}, 200


@app.route("/api/admin-search")
@auth_required("token")
@roles_required("admin")
def admin_search():
    qtype = request.args.get("query_type")
    q = request.args.get("query", "")

    if qtype == "student":
        students = StudentProfile.query.filter(
            or_(StudentProfile.name.contains(q), StudentProfile.email.contains(q),
                StudentProfile.roll_number.contains(q))
        ).all()
        return [{"student_id": s.id, "Student Name": s.name, "Student Email": s.email,
                 "Branch": s.branch, "CGPA": s.cgpa, "Year": s.year,
                 "Skills": s.skills, "Status": s.status} for s in students], 200

    elif qtype == "company":
        companies = CompanyProfile.query.filter(
            or_(CompanyProfile.name.contains(q), CompanyProfile.email.contains(q),
                CompanyProfile.industry.contains(q))
        ).all()
        return [{"company_id": c.id, "Company Name": c.name, "Company Email": c.email,
                 "Industry": c.industry, "Location": c.location, "Status": c.status} for c in companies], 200

    return {"message": "Invalid query type"}, 400


@app.route("/api/all-placements")
@auth_required("token")
@roles_required("admin")
def all_placements():
    result = []
    for p in Placement.query.all():
        student = StudentProfile.query.filter_by(user_id=p.student_id).first()
        company = CompanyProfile.query.filter_by(user_id=p.company_id).first()
        result.append({
            "Student Name": student.name if student else "N/A",
            "Company Name": company.name if company else "N/A",
            "Position": p.position, "Salary": p.salary,
            "Joining Date": str(p.joining_date) if p.joining_date else None,
            "Offer Letter": p.offer_letter_url
        })
    return result, 200


@app.route("/api/all-applications")
@auth_required("token")
@roles_required("admin")
def all_applications():
    applications = Application.query.all()
    result = []
    for a in applications:
        student = StudentProfile.query.filter_by(user_id=a.student_id).first()
        drive = PlacementDrive.query.get(a.drive_id)
        company = CompanyProfile.query.filter_by(user_id=drive.company_id).first() if drive else None
        result.append({
            "application_id": a.id,
            "Student Name": student.name if student else "N/A",
            "Student Email": student.email if student else "",
            "Branch": student.branch if student else "",
            "CGPA": student.cgpa if student else "",
            "Company Name": company.name if company else "N/A",
            "Job Title": drive.job_title if drive else "N/A",
            "Package": drive.package if drive else "",
            "Applied At": str(a.applied_at),
            "Status": a.status,
            "Interview Date": str(a.interview_date) if a.interview_date else None,
        })
    return result, 200


# ══════════════════════════════════════════════════════════════
#  COMPANY
# ══════════════════════════════════════════════════════════════

@app.route("/api/company-profile")
@auth_required("token")
@roles_required("company")
def company_profile():
    c = CompanyProfile.query.filter_by(user_id=current_user.id).first_or_404()
    return {"name": c.name, "email": c.email, "hr_contact": c.hr_contact,
            "website": c.website, "description": c.description,
            "industry": c.industry, "location": c.location, "status": c.status}, 200


@app.route("/api/create-drive", methods=["POST"])
@auth_required("token")
@roles_required("company")
def create_drive():
    c = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    if not c or c.status != "Approved":
        return {"message": "Your company is not approved yet"}, 403

    data = request.json
    d = PlacementDrive(
        job_title=data["job_title"], job_description=data.get("job_description", ""),
        skills_required=data.get("skills_required", ""),
        experience_required=data.get("experience_required", ""),
        package=data.get("package", ""), benefits=data.get("benefits", ""),
        location=data.get("location", ""),
        eligible_branches=data.get("eligible_branches", ""),
        min_cgpa=float(data.get("min_cgpa", 0)),
        eligible_years=data.get("eligible_years", ""),
        application_deadline=_parse_date(data.get("application_deadline")),
        drive_date=_parse_date(data.get("drive_date")),
        company_id=current_user.id
    )
    db.session.add(d)
    db.session.commit()
    return {"message": "Drive created. Awaiting admin approval."}, 201


@app.route("/api/close-drive/<int:did>")
@auth_required("token")
@roles_required("company")
def close_drive(did):
    d = PlacementDrive.query.filter_by(id=did, company_id=current_user.id).first_or_404()
    d.status = "Closed"
    db.session.commit()
    return {"message": "Drive closed"}, 200


@app.route("/api/get-drives")
@auth_required("token")
def get_drives():
    role = current_user.roles[0].name

    if role == "company":
        drives = PlacementDrive.query.filter_by(company_id=current_user.id).all()
        return [_drive_dict_simple(d) for d in drives], 200

    elif role == "student":
        student = StudentProfile.query.filter_by(user_id=current_user.id).first()
        applied_ids = {a.drive_id for a in Application.query.filter_by(student_id=current_user.id).all()}
        q = request.args.get("q", "")
        query = PlacementDrive.query.filter_by(status="Approved")
        if q:
            query = query.filter(or_(
                PlacementDrive.job_title.contains(q),
                PlacementDrive.skills_required.contains(q),
                PlacementDrive.location.contains(q)
            ))
        result = []
        for d in query.all():
            company = CompanyProfile.query.filter_by(user_id=d.company_id).first()
            item = _drive_dict(d, company)
            item["applied"] = d.id in applied_ids
            item["eligible"] = _check_eligibility(student, d)
            result.append(item)
        return result, 200

    return [], 200


@app.route("/api/drive-applications/<int:did>")
@auth_required("token")
@roles_required("company")
def drive_applications(did):
    d = PlacementDrive.query.filter_by(id=did, company_id=current_user.id).first_or_404()
    result = {s: [] for s in ["Applied", "Shortlisted", "Interview", "Offer", "Placed", "Rejected"]}
    for a in d.applications:
        s = StudentProfile.query.filter_by(user_id=a.student_id).first()
        entry = {
            "application_id": a.id,
            "Student Name": s.name if s else "N/A", "Student Email": s.email if s else "",
            "Branch": s.branch if s else "", "CGPA": s.cgpa if s else 0,
            "Year": s.year if s else 0, "Skills": s.skills if s else "",
            "Experience": s.experience if s else "", "Resume URL": s.resume_url if s else "",
            "Applied At": str(a.applied_at), "Status": a.status,
            "Interview Date": str(a.interview_date) if a.interview_date else None,
            "Interview Time": a.interview_time, "Interview Venue": a.interview_venue,
            "Notes": a.notes
        }
        if a.status in result:
            result[a.status].append(entry)
    return result, 200


@app.route("/api/update-application/<int:aid>", methods=["POST"])
@auth_required("token")
@roles_required("company")
def update_application(aid):
    a = Application.query.get_or_404(aid)
    drive = PlacementDrive.query.filter_by(id=a.drive_id, company_id=current_user.id).first_or_404()

    data = request.json
    status = data.get("status")
    valid = ["Applied", "Shortlisted", "Interview", "Offer", "Placed", "Rejected"]
    if status not in valid:
        return {"message": "Invalid status"}, 400

    a.status = status
    if data.get("notes"): a.notes = data["notes"]
    if data.get("interview_date"): a.interview_date = _parse_date(data["interview_date"])
    if data.get("interview_time"): a.interview_time = data["interview_time"]
    if data.get("interview_venue"): a.interview_venue = data["interview_venue"]

    if status == "Placed":
        if not Placement.query.filter_by(student_id=a.student_id, drive_id=a.drive_id).first():
            db.session.add(Placement(
                student_id=a.student_id, company_id=current_user.id, drive_id=a.drive_id,
                position=drive.job_title, salary=drive.package,
                joining_date=_parse_date(data.get("joining_date")),
                offer_letter_url=data.get("offer_letter_url", ""),
                created_at=date.today()
            ))
    db.session.commit()
    return {"message": f"Status updated to {status}"}, 200


# ══════════════════════════════════════════════════════════════
#  STUDENT
# ══════════════════════════════════════════════════════════════

@app.route("/api/student-profile")
@auth_required("token")
@roles_required("student")
def student_profile():
    s = StudentProfile.query.filter_by(user_id=current_user.id).first_or_404()
    return {"name": s.name, "email": s.email, "mobile": s.mobile, "branch": s.branch,
            "cgpa": s.cgpa, "year": s.year, "roll_number": s.roll_number,
            "resume_url": s.resume_url, "skills": s.skills,
            "experience": s.experience, "status": s.status}, 200


@app.route("/api/update-student-profile", methods=["POST"])
@auth_required("token")
@roles_required("student")
def update_student_profile():
    s = StudentProfile.query.filter_by(user_id=current_user.id).first_or_404()
    data = request.json
    for field in ["mobile", "branch", "resume_url", "skills", "experience"]:
        if data.get(field) is not None: setattr(s, field, data[field])
    if data.get("cgpa") is not None: s.cgpa = float(data["cgpa"])
    if data.get("year") is not None: s.year = int(data["year"])
    db.session.commit()
    return {"message": "Profile updated"}, 200


@app.route("/api/apply-drive/<int:did>", methods=["POST"])
@auth_required("token")
@roles_required("student")
def apply_drive(did):
    student = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not student or student.status == "Blacklisted":
        return {"message": "You are not eligible to apply"}, 403

    drive = PlacementDrive.query.get_or_404(did)
    if drive.status != "Approved":
        return {"message": "Drive is not available"}, 400
    if drive.application_deadline and drive.application_deadline < date.today():
        return {"message": "Application deadline has passed"}, 400
    if not _check_eligibility(student, drive):
        return {"message": "You do not meet the eligibility criteria"}, 400
    if Application.query.filter_by(student_id=current_user.id, drive_id=did).first():
        return {"message": "Already applied"}, 400

    db.session.add(Application(student_id=current_user.id, drive_id=did, applied_at=date.today()))
    db.session.commit()
    return {"message": "Applied successfully"}, 201


@app.route("/api/my-applications")
@auth_required("token")
@roles_required("student")
def my_applications():
    result = {s: [] for s in ["Applied", "Shortlisted", "Interview", "Offer", "Placed", "Rejected"]}
    for a in Application.query.filter_by(student_id=current_user.id).all():
        drive = PlacementDrive.query.get(a.drive_id)
        company = CompanyProfile.query.filter_by(user_id=drive.company_id).first() if drive else None
        entry = {
            "application_id": a.id, "drive_id": a.drive_id,
            "Job Title": drive.job_title if drive else "N/A",
            "Company Name": company.name if company else "N/A",
            "Package": drive.package if drive else "",
            "Location": drive.location if drive else "",
            "Applied At": str(a.applied_at), "Status": a.status,
            "Interview Date": str(a.interview_date) if a.interview_date else None,
            "Interview Time": a.interview_time, "Interview Venue": a.interview_venue,
            "Notes": a.notes
        }
        if a.status in result:
            result[a.status].append(entry)
    return result, 200


@app.route("/api/my-placements")
@auth_required("token")
@roles_required("student")
def my_placements():
    result = []
    for p in Placement.query.filter_by(student_id=current_user.id).all():
        company = CompanyProfile.query.filter_by(user_id=p.company_id).first()
        result.append({
            "Company Name": company.name if company else "N/A",
            "Position": p.position, "Salary": p.salary,
            "Joining Date": str(p.joining_date) if p.joining_date else None,
            "Offer Letter URL": p.offer_letter_url
        })
    return result, 200


# ══════════════════════════════════════════════════════════════
#  CELERY TASK ROUTES
# ══════════════════════════════════════════════════════════════

from .task import add_together, student_csv, company_csv, send_interview_reminders, send_monthly_report
from celery.result import AsyncResult


@app.route("/starttask")
def start_task():
    result = add_together.delay(5, 6)
    return {"result_id": result.id}


# @app.route("/result/<id>")
# def get_result(id):  
#     result = AsyncResult(id)
#     return {"ready": result.ready(), "successful": result.successful(), "value": result.result if result.ready() else None}

@app.route("/exportstudentcsv")
@auth_required("token")
@roles_required("student")
def export_student_csv():
    result = student_csv.delay(current_user.id)
    return {"task_id": result.id}


@app.route("/exportcompanycsv")
@auth_required("token")
@roles_required("company")
def export_company_csv():
    result = company_csv.delay(current_user.id)
    return {"result_id": result.id}



def _parse_date(val):
    if not val:
        return None
    try:
        return datetime.strptime(val, "%Y-%m-%d").date()
    except Exception:
        return None


def _check_eligibility(student, drive):
    if not student:
        return False
    branches = [b.strip() for b in (drive.eligible_branches or "").split(",") if b.strip()]
    years = [int(y.strip()) for y in (drive.eligible_years or "").split(",") if y.strip().isdigit()]
    return (not branches or student.branch in branches) and \
           (not years or student.year in years) and \
           (student.cgpa >= (drive.min_cgpa or 0))


def _drive_dict(drive, company):
    return {
        "drive_id": drive.id,
        "Job Title": drive.job_title, "Job Description": drive.job_description,
        "Skills Required": drive.skills_required, "Experience Required": drive.experience_required,
        "Package": drive.package, "Benefits": drive.benefits, "Location": drive.location,
        "Eligible Branches": drive.eligible_branches, "Min CGPA": drive.min_cgpa,
        "Eligible Years": drive.eligible_years,
        "Application Deadline": str(drive.application_deadline) if drive.application_deadline else None,
        "Drive Date": str(drive.drive_date) if drive.drive_date else None,
        "Status": drive.status,
        "Company Name": company.name if company else "N/A",
        "Industry": company.industry if company else "",
        "Applicant Count": len(drive.applications)
    }


def _drive_dict_simple(drive):
    return {
        "drive_id": drive.id, "job_title": drive.job_title,
        "job_description": drive.job_description,
        "skills_required": drive.skills_required,
        "experience_required": drive.experience_required,
        "package": drive.package, "benefits": drive.benefits,
        "location": drive.location, "eligible_branches": drive.eligible_branches,
        "min_cgpa": drive.min_cgpa, "eligible_years": drive.eligible_years,
        "application_deadline": str(drive.application_deadline) if drive.application_deadline else None,
        "drive_date": str(drive.drive_date) if drive.drive_date else None,
        "status": drive.status, "applicant_count": len(drive.applications)
    }

@app.route("/checkexport/<result_id>")
@auth_required("token")
def check_export(result_id):
    import os
    # Use current_app.celery (set in app.py) so we never do a runtime import
    # inside the request handler — that was causing the AssertionError:
    # "Popped wrong app context".
    try:
        result = current_app.celery.AsyncResult(result_id)
        state = result.state
        if state == "SUCCESS":
            filename = os.path.basename(str(result.result))
            return {"ready": True, "filename": filename}
        elif state == "FAILURE":
            return {"ready": False, "error": "Task failed"}, 500
        return {"ready": False, "state": state}
    except Exception as e:
        return {"ready": False, "error": str(e)}, 503


# @app.route("/downloadcsv/<filename>")
# def download_csv(filename):
#     from flask import send_from_directory, request as req
#     import os
#     # Accept token from query param since browser <a> tags cannot send headers
#     token = req.args.get("token")
#     if not token:
#         return {"message": "Auth Required"}, 401
#     static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
#     return send_from_directory(static_dir, filename, as_attachment=True)



@app.route("/result/<id>")
def download_csv(id):
    import os
    result = AsyncResult(id)

    if not result.ready():
        return {"message": "CSV generation is in progress"}, 202
    else:
        filename = os.path.basename(str(result.result))
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
        return send_from_directory(static_dir, filename, as_attachment=True), 200