from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TimeField, FloatField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange


class ExamForm(FlaskForm):
    name = StringField('Exam Title (e.g. Mid-Term Examination 2026)', validators=[DataRequired()])
    exam_type = SelectField('Exam Type', choices=[
        ('Midterm', 'Mid-Term Examination'),
        ('Internal', 'Internal Assessment / Unit Test'),
        ('Practical', 'Practical Examination / Lab Viva'),
        ('End Semester', 'End-Semester University Exam')
    ], default='Midterm')
    
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    semester_id = SelectField('Semester', coerce=int, validators=[DataRequired()])
    session_id = SelectField('Academic Session', coerce=int, validators=[DataRequired()])
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    class_division_id = SelectField('Target Division (Optional)', coerce=int, validators=[Optional()])
    
    exam_date = DateField('Date of Exam', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    room_number = StringField('Exam Hall / Room', validators=[Optional()])
    max_marks = FloatField('Maximum Marks', default=100.0, validators=[DataRequired(), NumberRange(min=1)])
    passing_marks = FloatField('Passing Marks', default=40.0, validators=[DataRequired(), NumberRange(min=1)])
    
    submit = SubmitField('Schedule Examination')
