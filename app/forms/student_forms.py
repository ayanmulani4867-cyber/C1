from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, DateField, FloatField, BooleanField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length, ValidationError
from app.extensions import db
from app.models.student import Student
from app.models.user import User


class StudentCreateForm(FlaskForm):
    # Credentials (Managed automatically by system)
    username = StringField('Username (Auto-generated from email)', validators=[Optional(), Length(max=64)])
    temporary_password = PasswordField('Initial Password (Auto-hashed from mobile number)', validators=[Optional()])
    auto_generate_credentials = BooleanField('Auto-generate login credentials', default=True)

    # Identifiers (Generated automatically server-side on creation)
    student_id = StringField('Student ID (Auto-generated)', validators=[Optional(), Length(max=30)])
    enrollment_no = StringField('Enrollment Number (Auto-generated)', validators=[Optional(), Length(max=30)])
    admission_no = StringField('Admission Number (Auto-generated)', validators=[Optional(), Length(max=30)])
    roll_no = StringField('Roll Number (Auto-generated)', validators=[Optional(), Length(max=30)])

    # Personal Information
    first_name = StringField('First Name', validators=[DataRequired(message="First name is required"), Length(max=50)])
    middle_name = StringField('Middle Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(message="Last name is required"), Length(max=50)])
    profile_photo = FileField('Profile Photo', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only (jpg, jpeg, png, webp)')])
    dob = DateField('Date of Birth', validators=[Optional()])
    gender = SelectField('Gender', choices=[('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired(message="Please select a gender")])
    blood_group = SelectField('Blood Group', choices=[('', 'Select Blood Group'), ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')], validators=[Optional()])
    nationality = StringField('Nationality', default='Indian', validators=[Optional()])
    personal_email = StringField('Personal Email', validators=[Optional(), Email(message="Enter a valid personal email address")])
    college_email = StringField('Official College Email', validators=[DataRequired(message="Official college email is required for student login"), Email(message="Enter a valid institutional email address")])
    mobile = StringField('Mobile Number', validators=[DataRequired(message="Mobile number is required (used as initial temporary password)"), Length(min=10, max=15, message="Mobile number must be 10-15 digits")])
    alt_mobile = StringField('Alternate Mobile Number', validators=[Optional(), Length(max=15)])

    # Academic Information
    department_id = SelectField('Department', coerce=int, validators=[DataRequired(message="Department selection is required")])
    course_id = SelectField('Course / Program', coerce=int, validators=[DataRequired(message="Course / Degree selection is required")])
    semester_id = SelectField('Semester', coerce=int, validators=[DataRequired(message="Semester selection is required")])
    session_id = SelectField('Academic Session', coerce=int, validators=[DataRequired(message="Academic session is required")])
    division_id = SelectField('Class Division', coerce=lambda x: int(x) if x and str(x).isdigit() else 0, validate_choice=False, validators=[Optional()])
    admission_date = DateField('Admission Date', validators=[Optional()])
    batch = StringField('Batch (e.g. 2024-2028)', validators=[Optional(), Length(max=30)])
    status = SelectField('Student Status', choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('Graduated', 'Graduated'), ('Transferred', 'Transferred')], default='Active')

    # Current Address
    curr_address_line1 = StringField('Address Line 1', validators=[Optional()])
    curr_address_line2 = StringField('Address Line 2', validators=[Optional()])
    curr_city = StringField('City', validators=[Optional()])
    curr_district = StringField('District', validators=[Optional()])
    curr_state = StringField('State', validators=[Optional()])
    curr_country = StringField('Country', default='India', validators=[Optional()])
    curr_pincode = StringField('PIN Code', validators=[Optional(), Length(max=10)])

    # Permanent Address
    same_as_current = BooleanField('Permanent address same as current address', default=False)
    perm_address_line1 = StringField('Address Line 1', validators=[Optional()])
    perm_address_line2 = StringField('Address Line 2', validators=[Optional()])
    perm_city = StringField('City', validators=[Optional()])
    perm_district = StringField('District', validators=[Optional()])
    perm_state = StringField('State', validators=[Optional()])
    perm_country = StringField('Country', default='India', validators=[Optional()])
    perm_pincode = StringField('PIN Code', validators=[Optional(), Length(max=10)])

    # Parent / Guardian Information
    father_name = StringField('Father / Guardian Name', validators=[Optional()])
    father_phone = StringField('Father / Guardian Phone', validators=[Optional()])
    father_email = StringField('Father / Guardian Email', validators=[Optional(), Email()])
    father_occupation = StringField('Father / Guardian Occupation', validators=[Optional()])

    mother_name = StringField('Mother Name', validators=[Optional()])
    mother_phone = StringField('Mother Phone', validators=[Optional()])
    mother_email = StringField('Mother Email', validators=[Optional(), Email()])
    mother_occupation = StringField('Mother Occupation', validators=[Optional()])

    # Emergency Contact
    emergency_name = StringField('Emergency Contact Name', validators=[Optional()])
    emergency_relation = StringField('Relationship', validators=[Optional()])
    emergency_phone = StringField('Emergency Phone Number', validators=[Optional()])
    emergency_alt_phone = StringField('Alternate Emergency Phone', validators=[Optional()])

    # Additional Information
    prev_qualification = StringField('Previous Qualification', validators=[Optional()])
    prev_institution = StringField('Previous Institution / School', validators=[Optional()])
    prev_percentage = FloatField('Previous Percentage / CGPA', validators=[Optional()])
    admission_type = SelectField('Admission Type', choices=[('Regular', 'Regular'), ('Lateral Entry', 'Lateral Entry'), ('Management Quota', 'Management Quota')], default='Regular')
    scholarship_status = SelectField('Scholarship Status', choices=[('None', 'None'), ('Merit Scholarship', 'Merit Scholarship'), ('Government Fee Reimbursement', 'Government Fee Reimbursement'), ('Sports Quota', 'Sports Quota')], default='None')
    hostel_status = SelectField('Hostel Status', choices=[('Day Scholar', 'Day Scholar'), ('Hosteller', 'Hosteller')], default='Day Scholar')
    transport_status = SelectField('Transport Status', choices=[('Self', 'Self'), ('College Bus', 'College Bus')], default='Self')

    submit = SubmitField('Register Student Profile')

    def validate_student_id(self, field):
        if field.data and field.data.strip():
            if Student.query.filter_by(student_id=field.data.strip()).first():
                raise ValidationError('A student with this Student ID already exists.')

    def validate_enrollment_no(self, field):
        if field.data and field.data.strip():
            if Student.query.filter_by(enrollment_no=field.data.strip()).first():
                raise ValidationError('A student with this Enrollment Number already exists.')

    def validate_admission_no(self, field):
        if field.data and field.data.strip():
            if Student.query.filter_by(admission_no=field.data.strip()).first():
                raise ValidationError('A student with this Admission Number already exists.')

    def validate_college_email(self, field):
        email_clean = field.data.strip().lower() if field.data else ''
        if not email_clean:
            return
        if User.query.filter(db.func.lower(User.email) == email_clean).first() or Student.query.filter(db.func.lower(Student.college_email) == email_clean).first():
            raise ValidationError('This official email address is already registered in the system.')


class StudentEditForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    middle_name = StringField('Middle Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    profile_photo = FileField('Change Profile Photo', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only')])
    roll_no = StringField('Roll Number', validators=[Optional(), Length(max=30)])
    batch = StringField('Batch / Academic Year', validators=[Optional(), Length(max=30)])
    admission_date = DateField('Admission Date', validators=[Optional()])
    
    dob = DateField('Date of Birth', validators=[Optional()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    blood_group = SelectField('Blood Group', choices=[('', 'Select Blood Group'), ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')], validators=[Optional()])
    nationality = StringField('Nationality', default='Indian', validators=[Optional()])
    personal_email = StringField('Personal Email', validators=[Optional(), Email()])
    mobile = StringField('Mobile Number', validators=[DataRequired(), Length(min=10, max=15)])
    alt_mobile = StringField('Alternate Mobile Number', validators=[Optional(), Length(max=15)])

    # Academic Fields (Admin-only editable)
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    course_id = SelectField('Course / Program', coerce=int, validators=[DataRequired()])
    semester_id = SelectField('Semester', coerce=int, validators=[DataRequired()])
    session_id = SelectField('Academic Session', coerce=int, validators=[DataRequired()])
    division_id = SelectField('Class Division', coerce=int, validators=[Optional()])
    status = SelectField('Status', choices=[('Active', 'Active'), ('Inactive', 'Inactive'), ('Graduated', 'Graduated'), ('Transferred', 'Transferred')])

    # Current Address
    curr_address_line1 = StringField('Address Line 1', validators=[Optional()])
    curr_address_line2 = StringField('Address Line 2', validators=[Optional()])
    curr_city = StringField('City', validators=[Optional()])
    curr_district = StringField('District', validators=[Optional()])
    curr_state = StringField('State', validators=[Optional()])
    curr_pincode = StringField('PIN Code', validators=[Optional()])

    # Permanent Address
    perm_address_line1 = StringField('Address Line 1', validators=[Optional()])
    perm_address_line2 = StringField('Address Line 2', validators=[Optional()])
    perm_city = StringField('City', validators=[Optional()])
    perm_district = StringField('District', validators=[Optional()])
    perm_state = StringField('State', validators=[Optional()])
    perm_pincode = StringField('PIN Code', validators=[Optional()])

    # Parent Details
    father_name = StringField('Father / Guardian Name', validators=[Optional()])
    father_phone = StringField('Father / Guardian Phone', validators=[Optional()])
    father_email = StringField('Father Email', validators=[Optional()])
    father_occupation = StringField('Father Occupation', validators=[Optional()])
    mother_name = StringField('Mother Name', validators=[Optional()])
    mother_phone = StringField('Mother Phone', validators=[Optional()])
    mother_email = StringField('Mother Email', validators=[Optional()])
    mother_occupation = StringField('Mother Occupation', validators=[Optional()])

    # Emergency Contact
    emergency_name = StringField('Emergency Contact Name', validators=[Optional()])
    emergency_relation = StringField('Relationship', validators=[Optional()])
    emergency_phone = StringField('Emergency Phone Number', validators=[Optional()])
    emergency_alt_phone = StringField('Alternate Emergency Phone', validators=[Optional()])

    # Academic Background & Status
    prev_qualification = StringField('Previous Qualification', validators=[Optional()])
    prev_institution = StringField('Previous School / College', validators=[Optional()])
    prev_percentage = FloatField('Previous Percentage / CGPA', validators=[Optional()])
    admission_type = SelectField('Admission Type', choices=[('Regular', 'Regular'), ('Lateral Entry', 'Lateral Entry'), ('Management Quota', 'Management Quota'), ('Transfer', 'Transfer')], validators=[Optional()])
    scholarship_status = SelectField('Scholarship Category', choices=[('None', 'None / Self-Financed'), ('Merit', 'Institute Merit Scholarship'), ('Government', 'State/National Scholarship'), ('Category', 'Reserved Category Aid')], validators=[Optional()])
    hostel_status = SelectField('Hostel Status', choices=[('Day Scholar', 'Day Scholar'), ('Hosteller', 'Hosteller')])
    transport_status = SelectField('Transport Status', choices=[('Self', 'Self / Own Transport'), ('College Bus', 'College Bus Transport')])

    submit = SubmitField('Update Student Profile')


class StudentDocumentForm(FlaskForm):
    doc_type = SelectField('Document Type', choices=[
        ('ID Proof', 'ID Proof / Aadhaar / Passport'),
        ('10th Marksheet', '10th Standard Marksheet'),
        ('12th Marksheet', '12th Standard Marksheet'),
        ('Admission Doc', 'Admission Confirmation Letter'),
        ('Transfer Certificate', 'Transfer Certificate (TC)'),
        ('Other', 'Other Document')
    ], validators=[DataRequired()])
    title = StringField('Document Title / Description', validators=[DataRequired(), Length(max=100)])
    document_file = FileField('Upload File (PDF/Image)', validators=[
        DataRequired(),
        FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF and Images only!')
    ])
    submit = SubmitField('Upload Document')
