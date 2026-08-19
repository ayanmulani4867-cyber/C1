from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, TextAreaField, BooleanField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Optional, Length, NumberRange, ValidationError
from app.models.department import Department
from app.models.course import Course
from app.models.subject import Subject


class DepartmentForm(FlaskForm):
    name = StringField('Department Name', validators=[DataRequired(), Length(max=100)])
    code = StringField('Department Code (e.g. CSE, ECE, ME)', validators=[DataRequired(), Length(max=20)])
    description = TextAreaField('Description / Objectives', validators=[Optional()])
    hod_faculty_id = SelectField('Appoint Head of Department (HOD)', coerce=int, validators=[Optional()])
    is_active = BooleanField('Department Active', default=True)
    submit = SubmitField('Save Department')


class CourseForm(FlaskForm):
    name = StringField('Course / Degree Name (e.g. B.Tech Computer Science)', validators=[DataRequired(), Length(max=120)])
    code = StringField('Course Code (e.g. BT-CSE)', validators=[DataRequired(), Length(max=30)])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    duration_years = IntegerField('Duration (Years)', default=4, validators=[DataRequired(), NumberRange(min=1, max=6)])
    total_semesters = IntegerField('Total Semesters', default=8, validators=[DataRequired(), NumberRange(min=1, max=12)])
    description = TextAreaField('Description', validators=[Optional()])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Course')


class SemesterForm(FlaskForm):
    number = IntegerField('Semester Number (1 to 12)', validators=[DataRequired(), NumberRange(min=1, max=12)])
    name = StringField('Semester Label (e.g. Semester 1)', validators=[DataRequired(), Length(max=50)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Semester')


class AcademicSessionForm(FlaskForm):
    name = StringField('Session Name (e.g. 2025-26)', validators=[DataRequired(), Length(max=50)])
    start_year = IntegerField('Start Year (e.g. 2025)', validators=[DataRequired(), NumberRange(min=2000, max=2100)])
    end_year = IntegerField('End Year (e.g. 2026)', validators=[DataRequired(), NumberRange(min=2000, max=2100)])
    is_current = BooleanField('Set as Current Active Academic Session', default=False)
    submit = SubmitField('Save Academic Session')


class ClassDivisionForm(FlaskForm):
    name = StringField('Division Section (e.g. A, B, C)', validators=[DataRequired(), Length(max=50)])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    course_id = SelectField('Course / Program', coerce=int, validators=[DataRequired()])
    semester_id = SelectField('Semester', coerce=int, validators=[DataRequired()])
    session_id = SelectField('Academic Session', coerce=int, validators=[DataRequired()])
    room_number = StringField('Designated Classroom / Lecture Hall', validators=[Optional(), Length(max=30)])
    submit = SubmitField('Save Class Division')


class SubjectForm(FlaskForm):
    name = StringField('Subject Name', validators=[DataRequired(), Length(max=120)])
    code = StringField('Subject Code (e.g. CS401)', validators=[DataRequired(), Length(max=30)])
    credits = IntegerField('Credits', default=3, validators=[DataRequired(), NumberRange(min=1, max=10)])
    subject_type = SelectField('Subject Type', choices=[('Theory', 'Theory'), ('Practical', 'Practical / Lab'), ('Elective', 'Elective')], default='Theory')
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    semester_id = SelectField('Semester', coerce=int, validators=[DataRequired()])
    assigned_faculty_ids = SelectMultipleField('Assign Faculty Member(s)', coerce=int, validators=[Optional()])
    submit = SubmitField('Save Subject')
