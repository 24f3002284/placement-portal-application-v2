from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()


class Role(db.Model, RoleMixin):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    fs_uniquifier = db.Column(db.String, unique=True, nullable=False)
    roles = db.relationship("Role", secondary="user_roles", backref="users")
    student_profile = db.relationship("StudentProfile", backref="user", uselist=False)
    company_profile = db.relationship("CompanyProfile", backref="user", uselist=False)
    drives = db.relationship("PlacementDrive", backref="company", foreign_keys="PlacementDrive.company_id")
    applications = db.relationship("Application", backref="student", foreign_keys="Application.student_id")


class UserRoles(db.Model):
    __tablename__ = "user_roles"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"))


class StudentProfile(db.Model):
    __tablename__ = "student_profile"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    mobile = db.Column(db.String)
    branch = db.Column(db.String)
    cgpa = db.Column(db.Float, default=0.0)
    year = db.Column(db.Integer)
    roll_number = db.Column(db.String)
    resume_url = db.Column(db.String, nullable=True)
    skills = db.Column(db.String, nullable=True)       # comma-separated e.g. "Python,Java,SQL"
    experience = db.Column(db.String, nullable=True)   # e.g. "1 year intern at XYZ Corp"
    status = db.Column(db.String, nullable=False, default="Active")  # Active / Blacklisted
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class CompanyProfile(db.Model):
    __tablename__ = "company_profile"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    hr_contact = db.Column(db.String)
    website = db.Column(db.String)
    description = db.Column(db.String)
    industry = db.Column(db.String)                    # e.g. "IT", "Finance", "Healthcare"
    location = db.Column(db.String)                    # company HQ location
    status = db.Column(db.String, nullable=False, default="Registered")  # Registered/Approved/Rejected/Blacklisted
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class PlacementDrive(db.Model):
    __tablename__ = "placement_drive"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_title = db.Column(db.String, nullable=False)
    job_description = db.Column(db.String)
    skills_required = db.Column(db.String)             # comma-separated e.g. "Python,React,SQL"
    experience_required = db.Column(db.String)         # e.g. "0-2 years", "Fresher"
    eligible_branches = db.Column(db.String)           # comma-separated e.g. "CSE,ECE"
    min_cgpa = db.Column(db.Float, default=0.0)
    eligible_years = db.Column(db.String)              # comma-separated e.g. "3,4"
    package = db.Column(db.String)                     # e.g. "12 LPA"
    benefits = db.Column(db.String)                    # e.g. "Health insurance, WFH, Bonus"
    location = db.Column(db.String)
    application_deadline = db.Column(db.Date, nullable=True)
    drive_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String, nullable=False, default="Pending")  # Pending/Approved/Rejected/Closed
    company_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    applications = db.relationship("Application", backref="drive", lazy=True)


class Application(db.Model):
    __tablename__ = "application"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drive.id"), nullable=False)
    applied_at = db.Column(db.Date, nullable=False)
    # Full status flow: Applied → Shortlisted → Interview → Offer → Placed / Rejected
    status = db.Column(db.String, nullable=False, default="Applied")
    interview_date = db.Column(db.Date, nullable=True)
    interview_time = db.Column(db.String, nullable=True)    # e.g. "10:00 AM"
    interview_venue = db.Column(db.String, nullable=True)   # e.g. "Zoom / Office Block B"
    notes = db.Column(db.String, nullable=True)             # feedback from company

    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='unique_student_drive'),)


class Placement(db.Model):
    """Confirmed placement record - created when Application.status set to 'Placed'"""
    __tablename__ = "placement"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drive.id"), nullable=False)
    position = db.Column(db.String, nullable=False)
    salary = db.Column(db.String)
    joining_date = db.Column(db.Date, nullable=True)
    offer_letter_url = db.Column(db.String, nullable=True)
    created_at = db.Column(db.Date, nullable=False)

    student = db.relationship("User", foreign_keys=[student_id], backref="placements_as_student")
    company_user = db.relationship("User", foreign_keys=[company_id], backref="placements_as_company")
    drive = db.relationship("PlacementDrive", backref="placements")
