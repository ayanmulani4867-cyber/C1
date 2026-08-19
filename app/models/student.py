from datetime import datetime
from app.extensions import db


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)

    # Identifiers
    student_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    enrollment_no = db.Column(db.String(30), unique=True, nullable=False, index=True)
    admission_no = db.Column(db.String(30), unique=True, nullable=False, index=True)
    roll_no = db.Column(db.String(30), nullable=True, index=True)

    # Personal Information
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(150), nullable=False, index=True)
    profile_photo = db.Column(db.String(255), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)  # Male, Female, Other
    blood_group = db.Column(db.String(10), nullable=True)
    nationality = db.Column(db.String(50), default='Indian', nullable=True)
    personal_email = db.Column(db.String(120), nullable=True)
    college_email = db.Column(db.String(120), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    alt_mobile = db.Column(db.String(20), nullable=True)

    # Academic Information
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='RESTRICT'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='RESTRICT'), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id', ondelete='RESTRICT'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('academic_sessions.id', ondelete='RESTRICT'), nullable=False)
    division_id = db.Column(db.Integer, db.ForeignKey('class_divisions.id', ondelete='RESTRICT'), nullable=True)
    admission_date = db.Column(db.Date, nullable=True)
    batch = db.Column(db.String(30), nullable=True)  # e.g., "2023-2027"
    status = db.Column(db.String(30), default='Active', nullable=False)  # Active, Inactive, Graduated, Transferred

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

    # Parent / Guardian Information
    father_name = db.Column(db.String(100), nullable=True)
    father_phone = db.Column(db.String(20), nullable=True)
    father_email = db.Column(db.String(120), nullable=True)
    father_occupation = db.Column(db.String(100), nullable=True)

    mother_name = db.Column(db.String(100), nullable=True)
    mother_phone = db.Column(db.String(20), nullable=True)
    mother_email = db.Column(db.String(120), nullable=True)
    mother_occupation = db.Column(db.String(100), nullable=True)

    # Emergency Contact
    emergency_name = db.Column(db.String(100), nullable=True)
    emergency_relation = db.Column(db.String(50), nullable=True)
    emergency_phone = db.Column(db.String(20), nullable=True)
    emergency_alt_phone = db.Column(db.String(20), nullable=True)

    # Additional Information
    prev_qualification = db.Column(db.String(100), nullable=True)  # Higher Secondary, Diploma, etc.
    prev_institution = db.Column(db.String(150), nullable=True)
    prev_percentage = db.Column(db.Float, nullable=True)
    admission_type = db.Column(db.String(50), default='Regular', nullable=True)  # Regular, Lateral Entry, Management Quota
    scholarship_status = db.Column(db.String(50), default='None', nullable=True)  # None, Merit, Government, Category
    hostel_status = db.Column(db.String(30), default='Day Scholar', nullable=True)  # Day Scholar, Hosteller
    transport_status = db.Column(db.String(30), default='Self', nullable=True)  # Self, College Bus

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships (backrefs provided by Department, Course, Semester, AcademicSession, ClassDivision)
    documents = db.relationship('StudentDocument', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    attendance_records = db.relationship('AttendanceRecord', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    exam_results = db.relationship('ExamResult', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    assignment_submissions = db.relationship('AssignmentSubmission', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    student_fees = db.relationship('StudentFee', backref='student_record', lazy='dynamic', cascade='all, delete-orphan', overlaps="fee_records,student")
    certificate_requests = db.relationship('CertificateRequest', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    complaints = db.relationship('Complaint', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    event_registrations = db.relationship('EventRegistration', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='student', lazy='dynamic')

    @property
    def roll_number(self):
        return self.roll_no or self.enrollment_no or str(self.id)

    @roll_number.setter
    def roll_number(self, val):
        self.roll_no = val

    @property
    def admission_number(self):
        return self.admission_no or self.student_id

    @admission_number.setter
    def admission_number(self, val):
        self.admission_no = val

    @property
    def enrollment_number(self):
        return self.enrollment_no or self.student_id

    @enrollment_number.setter
    def enrollment_number(self, val):
        self.enrollment_no = val

    @property
    def photo(self):
        return self.profile_photo

    @photo.setter
    def photo(self, val):
        self.profile_photo = val

    @property
    def profile_image_url(self):
        if self.profile_photo:
            if self.profile_photo.startswith('http://') or self.profile_photo.startswith('https://') or self.profile_photo.startswith('/'):
                return self.profile_photo
            return f"/static/{self.profile_photo}"
        name = self.full_name or f"{self.first_name} {self.last_name}"
        return f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}&background=0f766e&color=ffffff&size=128&bold=true"

    @property
    def class_division_id(self):
        return self.division_id

    @class_division_id.setter
    def class_division_id(self, val):
        self.division_id = val

    @property
    def admission_category(self):
        return self.admission_type or 'General'

    @admission_category.setter
    def admission_category(self, val):
        self.admission_type = val

    @property
    def official_email(self):
        return self.college_email

    @official_email.setter
    def official_email(self, val):
        self.college_email = val

    @property
    def class_division_id(self):
        return self.division_id

    @class_division_id.setter
    def class_division_id(self, val):
        self.division_id = val

    @property
    def class_division(self):
        return self.division

    @property
    def current_address(self):
        return type('Addr', (), {
            'line1': self.curr_address_line1 or '',
            'line2': self.curr_address_line2 or '',
            'city': self.curr_city or '',
            'district': self.curr_district or '',
            'state': self.curr_state or '',
            'country': self.curr_country or 'India',
            'pincode': self.curr_pincode or ''
        })()

    @property
    def permanent_address(self):
        return type('Addr', (), {
            'line1': self.perm_address_line1 or '',
            'line2': self.perm_address_line2 or '',
            'city': self.perm_city or '',
            'district': self.perm_district or '',
            'state': self.perm_state or '',
            'country': self.perm_country or 'India',
            'pincode': self.perm_pincode or ''
        })()

    @property
    def parent_info(self):
        return self

    @property
    def emergency_contact(self):
        return self

    @property
    def address(self):
        return self

    def __repr__(self):
        return f'<Student {self.student_id} - {self.full_name}>'


class Address:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class ParentInfo:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class EmergencyContact:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class StudentDocument(db.Model):
    __tablename__ = 'student_documents'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    doc_type = db.Column(db.String(50), nullable=False)  # ID Proof, 10th Marksheet, 12th Marksheet, Admission Doc, Transfer Certificate, Other
    title = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    uploaded_by = db.Column(db.String(50), default='Admin', nullable=False)
    verification_status = db.Column(db.String(30), default='Verified', nullable=False)  # Pending, Verified, Rejected

    def __repr__(self):
        return f'<StudentDocument {self.doc_type} - {self.title}>'
