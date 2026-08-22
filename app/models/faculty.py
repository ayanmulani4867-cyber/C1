from datetime import datetime
from app.extensions import db

# Association table for Faculty - Class Division assignments (many-to-many)
faculty_classes = db.Table(
    'faculty_classes',
    db.Column('faculty_id', db.Integer, db.ForeignKey('faculty.id', ondelete='CASCADE'), primary_key=True),
    db.Column('class_division_id', db.Integer, db.ForeignKey('class_divisions.id', ondelete='CASCADE'), primary_key=True)
)


class Faculty(db.Model):
    __tablename__ = 'faculty'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    # Personal Identifiers
    faculty_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    employee_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(150), nullable=False, index=True)
    profile_photo = db.Column(db.String(255), nullable=True)
    
    # Personal Info
    dob = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)  # Male, Female, Other
    blood_group = db.Column(db.String(10), nullable=True)
    personal_email = db.Column(db.String(120), nullable=True)
    official_email = db.Column(db.String(120), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    alt_mobile = db.Column(db.String(20), nullable=True)

    # Professional Info
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='RESTRICT'), nullable=False)
    designation = db.Column(db.String(100), default='Assistant Professor', nullable=False)  # Professor, Associate Professor, Assistant Professor, Lecturer
    employment_type = db.Column(db.String(30), default='Permanent', nullable=False)  # Permanent, Contract, Visiting, Guest
    joining_date = db.Column(db.Date, nullable=True)
    qualification = db.Column(db.String(150), nullable=True)  # Ph.D, M.Tech, M.Sc, etc.
    specialization = db.Column(db.String(150), nullable=True)
    experience_years = db.Column(db.Float, default=0.0, nullable=True)
    status = db.Column(db.String(30), default='Active', nullable=False)  # Active, Inactive, On Leave, Retired

    # Current Address
    curr_address_line1 = db.Column(db.String(200), nullable=True)
    curr_address_line2 = db.Column(db.String(200), nullable=True)
    curr_city = db.Column(db.String(100), nullable=True)
    curr_district = db.Column(db.String(100), nullable=True)
    curr_state = db.Column(db.String(100), nullable=True)
    curr_country = db.Column(db.String(100), default='India', nullable=True)
    curr_pincode = db.Column(db.String(20), nullable=True)

    # Permanent Address
    perm_address_line1 = db.Column(db.String(200), nullable=True)
    perm_address_line2 = db.Column(db.String(200), nullable=True)
    perm_city = db.Column(db.String(100), nullable=True)
    perm_district = db.Column(db.String(100), nullable=True)
    perm_state = db.Column(db.String(100), nullable=True)
    perm_country = db.Column(db.String(100), default='India', nullable=True)
    perm_pincode = db.Column(db.String(20), nullable=True)

    # Emergency Contact
    emergency_name = db.Column(db.String(100), nullable=True)
    emergency_relation = db.Column(db.String(50), nullable=True)
    emergency_phone = db.Column(db.String(20), nullable=True)
    emergency_alt_phone = db.Column(db.String(20), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships (backref 'department' provided by Department.faculty_members)
    assigned_classes = db.relationship('ClassDivision', secondary=faculty_classes, backref=db.backref('assigned_faculty', lazy='dynamic'))
    timetables = db.relationship('Timetable', backref='faculty', lazy='dynamic')
    attendance_sessions = db.relationship('AttendanceSession', backref='faculty', lazy='dynamic')
    assignments = db.relationship('Assignment', backref='faculty', lazy='dynamic')
    study_materials = db.relationship('StudyMaterial', backref='faculty', lazy='dynamic')
    documents = db.relationship('FacultyDocument', backref='faculty', lazy='dynamic', cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='target_faculty', lazy='dynamic')

    @property
    def date_of_joining(self):
        return self.joining_date

    @date_of_joining.setter
    def date_of_joining(self, val):
        self.joining_date = val

    @property
    def photo(self):
        return self.profile_photo

    @photo.setter
    def photo(self, val):
        self.profile_photo = val

    @property
    def profile_image_url(self):
        from app.utils.uploads import format_profile_image_url
        return format_profile_image_url(self.profile_photo, name=self.full_name or f"{self.first_name} {self.last_name}", bg_color="1e3a8a")

    @property
    def subjects(self):
        from app.models.subject import Subject
        from app.models.timetable import Timetable
        subject_ids = [t.subject_id for t in Timetable.query.filter_by(faculty_id=self.id).all() if t.subject_id]
        if subject_ids:
            return Subject.query.filter(Subject.id.in_(set(subject_ids))).all()
        return Subject.query.filter_by(department_id=self.department_id).limit(6).all()

    @property
    def address(self):
        return self

    @property
    def emergency_contact(self):
        return self

    def __repr__(self):
        return f'<Faculty {self.faculty_id} - {self.full_name}>'


class FacultyAddress:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class FacultyEmergencyContact:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class FacultyDocument(db.Model):
    __tablename__ = 'faculty_documents'

    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='CASCADE'), nullable=False)
    doc_type = db.Column(db.String(50), nullable=False)  # Resume, ID Proof, Degree Certificate, Experience Letter, Other
    title = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    verification_status = db.Column(db.String(30), default='Verified', nullable=False)  # Pending, Verified, Rejected

    @property
    def uploaded_at(self):
        return self.upload_date

    @property
    def is_verified(self):
        return self.verification_status == 'Verified'

    @property
    def document_url(self):
        from app.utils.uploads import format_document_url
        return format_document_url(self.file_path)

    def __repr__(self):
        return f'<FacultyDocument {self.doc_type} - {self.title}>'

