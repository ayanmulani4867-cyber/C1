from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, DateField, FloatField, BooleanField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length, ValidationError
from app.extensions import db
from app.models.faculty import Faculty
from app.models.user import User


class FacultyCreateForm(FlaskForm):
    # Credentials (Managed automatically)
    username = StringField('Username (Auto-generated from email)', validators=[Optional(), Length(max=64)])
    temporary_password = PasswordField('Initial Password (Auto-hashed from mobile number)', validators=[Optional()])
    auto_generate_credentials = BooleanField('Auto-generate login credentials', default=True)

    # Identifiers (Generated automatically server-side on creation)
    faculty_id = StringField('Faculty / Employee ID (Auto-generated)', validators=[Optional(), Length(max=30)])
    employee_id = StringField('Employee ID (Auto-generated)', validators=[Optional(), Length(max=30)])
    first_name = StringField('First Name', validators=[DataRequired(message="First name is required"), Length(max=50)])
    middle_name = StringField('Middle Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(message="Last name is required"), Length(max=50)])
    profile_photo = FileField('Profile Photo', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only (jpg, jpeg, png, webp)')])

    # Personal Information
    dob = DateField('Date of Birth', validators=[Optional()])
    gender = SelectField('Gender', choices=[('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired(message="Please select gender")])
    blood_group = SelectField('Blood Group', choices=[('', 'Select Blood Group'), ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')], validators=[Optional()])
    personal_email = StringField('Personal Email', validators=[Optional(), Email(message="Enter a valid personal email")])
    official_email = StringField('Official Institute Email', validators=[DataRequired(message="Official institute email is required for faculty login"), Email(message="Enter a valid official email")])
    mobile = StringField('Mobile Number', validators=[DataRequired(message="Mobile number is required (used as initial temporary password)"), Length(min=10, max=15, message="Mobile number must be 10-15 digits")])
    alt_mobile = StringField('Alternate Mobile Number', validators=[Optional(), Length(max=15)])

    # Professional Information
    department_id = SelectField('Department', coerce=int, validators=[DataRequired(message="Department is required")])
    designation = SelectField('Designation', choices=[
        ('Professor', 'Professor'),
        ('Associate Professor', 'Associate Professor'),
        ('Assistant Professor', 'Assistant Professor'),
        ('Lecturer', 'Lecturer'),
        ('Adjunct Faculty', 'Adjunct Faculty'),
        ('Visiting Faculty', 'Visiting Faculty')
    ], default='Assistant Professor')
    employment_type = SelectField('Employment Type', choices=[
        ('Permanent', 'Permanent'),
        ('Contract', 'Contract'),
        ('Visiting', 'Visiting'),
        ('Guest', 'Guest')
    ], default='Permanent')
    joining_date = DateField('Date of Joining', validators=[Optional()])
    qualification = StringField('Highest Qualification (e.g. Ph.D, M.Tech)', validators=[Optional(), Length(max=150)])
    specialization = StringField('Specialization / Research Area', validators=[Optional(), Length(max=150)])
    experience_years = FloatField('Total Experience (Years)', validators=[Optional()], default=0.0)
    status = SelectField('Faculty Status', choices=[
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('On Leave', 'On Leave'),
        ('Retired', 'Retired')
    ], default='Active')

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

    # Emergency Contact
    emergency_name = StringField('Emergency Contact Name', validators=[Optional()])
    emergency_relation = StringField('Relationship', validators=[Optional()])
    emergency_phone = StringField('Emergency Phone Number', validators=[Optional()])
    emergency_alt_phone = StringField('Alternate Emergency Phone', validators=[Optional()])

    submit = SubmitField('Register Faculty Member')

    def validate_faculty_id(self, field):
        if field.data and field.data.strip():
            if Faculty.query.filter_by(faculty_id=field.data.strip()).first():
                raise ValidationError('A faculty member with this Faculty ID already exists.')

    def validate_employee_id(self, field):
        if field.data and field.data.strip():
            if Faculty.query.filter_by(employee_id=field.data.strip()).first():
                raise ValidationError('A faculty member with this Employee ID already exists.')

    def validate_official_email(self, field):
        email_clean = field.data.strip().lower() if field.data else ''
        if not email_clean:
            return
        if User.query.filter(db.func.lower(User.email) == email_clean).first() or Faculty.query.filter(db.func.lower(Faculty.official_email) == email_clean).first():
            raise ValidationError('This official email address is already registered.')


class FacultyEditForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    middle_name = StringField('Middle Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    profile_photo = FileField('Change Profile Photo', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only')])
    
    dob = DateField('Date of Birth', validators=[Optional()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], validators=[DataRequired()])
    blood_group = SelectField('Blood Group', choices=[('', 'Select Blood Group'), ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')], validators=[Optional()])
    personal_email = StringField('Personal Email', validators=[Optional(), Email()])
    mobile = StringField('Mobile Number', validators=[DataRequired(), Length(min=10, max=15)])
    alt_mobile = StringField('Alternate Mobile Number', validators=[Optional(), Length(max=15)])

    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    designation = SelectField('Designation', choices=[
        ('Professor', 'Professor'),
        ('Associate Professor', 'Associate Professor'),
        ('Assistant Professor', 'Assistant Professor'),
        ('Lecturer', 'Lecturer'),
        ('Adjunct Faculty', 'Adjunct Faculty'),
        ('Visiting Faculty', 'Visiting Faculty')
    ])
    employment_type = SelectField('Employment Type', choices=[
        ('Permanent', 'Permanent'),
        ('Contract', 'Contract'),
        ('Visiting', 'Visiting'),
        ('Guest', 'Guest')
    ])
    qualification = StringField('Qualification', validators=[Optional(), Length(max=150)])
    specialization = StringField('Specialization', validators=[Optional(), Length(max=150)])
    experience_years = FloatField('Experience (Years)', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('On Leave', 'On Leave'),
        ('Retired', 'Retired')
    ])

    curr_address_line1 = StringField('Address Line 1', validators=[Optional()])
    curr_address_line2 = StringField('Address Line 2', validators=[Optional()])
    curr_city = StringField('City', validators=[Optional()])
    curr_district = StringField('District', validators=[Optional()])
    curr_state = StringField('State', validators=[Optional()])
    curr_pincode = StringField('PIN Code', validators=[Optional()])

    perm_address_line1 = StringField('Address Line 1', validators=[Optional()])
    perm_address_line2 = StringField('Address Line 2', validators=[Optional()])
    perm_city = StringField('City', validators=[Optional()])
    perm_district = StringField('District', validators=[Optional()])
    perm_state = StringField('State', validators=[Optional()])
    perm_pincode = StringField('PIN Code', validators=[Optional()])

    emergency_name = StringField('Emergency Contact Name', validators=[Optional()])
    emergency_relation = StringField('Relationship', validators=[Optional()])
    emergency_phone = StringField('Emergency Phone Number', validators=[Optional()])
    emergency_alt_phone = StringField('Alternate Emergency Phone', validators=[Optional()])

    submit = SubmitField('Update Faculty Profile')


class FacultyDocumentForm(FlaskForm):
    doc_type = SelectField('Document Type', choices=[
        ('Resume', 'Curriculum Vitae / Resume'),
        ('ID Proof', 'Aadhaar / Passport / Voter ID'),
        ('Degree Certificate', 'Ph.D / Master Degree Certificate'),
        ('Experience Letter', 'Previous Experience Certificate'),
        ('Other', 'Other Document')
    ], validators=[DataRequired()])
    title = StringField('Document Title', validators=[DataRequired(), Length(max=100)])
    document_file = FileField('Upload File', validators=[
        DataRequired(),
        FileAllowed(['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'], 'Allowed: PDF, Images, DOC, DOCX')
    ])
    submit = SubmitField('Upload Document')
