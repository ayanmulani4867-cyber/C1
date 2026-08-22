from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager


class Role:
    ADMIN = 'ADMIN'
    HOD = 'HOD'
    FACULTY = 'FACULTY'
    STUDENT = 'STUDENT'

    CHOICES = [
        (ADMIN, 'Administrator'),
        (HOD, 'Head of Department'),
        (FACULTY, 'Faculty Member'),
        (STUDENT, 'Student'),
    ]

    ALL = [ADMIN, HOD, FACULTY, STUDENT]


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='STUDENT')  # ADMIN, HOD, FACULTY, STUDENT
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    must_change_password = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    student_profile = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    faculty_profile = db.relationship('Faculty', backref='user', uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    leave_requests = db.relationship('LeaveRequest', foreign_keys='LeaveRequest.user_id', backref='applicant', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def verify_password(self, password):
        return self.check_password(password)

    @classmethod
    def get_by_identifier(cls, identifier):
        if not identifier:
            return None
        ident_str = str(identifier).strip()
        ident_lower = ident_str.lower()

        # 1. Primary lookup by username or email
        user = cls.query.filter(
            (db.func.lower(cls.username) == ident_lower) | 
            (db.func.lower(cls.email) == ident_lower)
        ).first()
        if user:
            return user

        # 2. Lookup by Student identifiers (student_id, admission_no, enrollment_no, college_email)
        try:
            from app.models.student import Student
            student = Student.query.filter(
                (db.func.lower(Student.student_id) == ident_lower) |
                (db.func.lower(Student.admission_no) == ident_lower) |
                (db.func.lower(Student.enrollment_no) == ident_lower) |
                (db.func.lower(Student.college_email) == ident_lower)
            ).first()
            if student and student.user:
                return student.user
        except Exception:
            pass

        # 3. Lookup by Faculty identifiers (employee_id, faculty_id, official_email)
        try:
            from app.models.faculty import Faculty
            faculty = Faculty.query.filter(
                (db.func.lower(Faculty.employee_id) == ident_lower) |
                (db.func.lower(Faculty.faculty_id) == ident_lower) |
                (db.func.lower(Faculty.official_email) == ident_lower)
            ).first()
            if faculty and faculty.user:
                return faculty.user
        except Exception:
            pass

        return None

    @property
    def is_admin(self):
        return str(self.role).strip().upper() == 'ADMIN' if self.role else False

    @property
    def is_hod(self):
        return str(self.role).strip().upper() == 'HOD' if self.role else False

    @property
    def is_faculty(self):
        return str(self.role).strip().upper() in ('FACULTY', 'HOD') if self.role else False

    @property
    def is_student(self):
        return str(self.role).strip().upper() == 'STUDENT' if self.role else False

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.student_profile and hasattr(self.student_profile, 'full_name'):
            return self.student_profile.full_name
        elif self.faculty_profile and hasattr(self.faculty_profile, 'full_name'):
            return self.faculty_profile.full_name
        return self.username

    @property
    def display_name(self):
        return self.full_name

    @property
    def profile_image_url(self):
        from app.utils.uploads import format_profile_image_url
        photo = self.profile_image
        if not photo and self.student_profile and self.student_profile.profile_photo:
            photo = self.student_profile.profile_photo
        elif not photo and self.faculty_profile and self.faculty_profile.profile_photo:
            photo = self.faculty_profile.profile_photo
        return format_profile_image_url(photo, name=self.full_name or self.username, bg_color="1e3a8a")

    def __repr__(self):
        return f'<User {self.username} [{self.role}]>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
