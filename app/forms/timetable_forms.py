from flask_wtf import FlaskForm
from wtforms import SelectField, TimeField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional


class TimetableForm(FlaskForm):
    day_of_week = SelectField('Day of Week', choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday')
    ], validators=[DataRequired()])
    start_time = TimeField('Class Start Time', validators=[DataRequired()])
    end_time = TimeField('Class End Time', validators=[DataRequired()])
    
    class_division_id = SelectField('Class Division', coerce=int, validators=[DataRequired()])
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    faculty_id = SelectField('Faculty Instructor', coerce=int, validators=[DataRequired()])
    semester_id = SelectField('Semester', coerce=int, validators=[DataRequired()])
    session_id = SelectField('Academic Session', coerce=int, validators=[DataRequired()])
    room_number = StringField('Classroom / Lab / Hall', validators=[DataRequired()])
    
    submit = SubmitField('Save Timetable Slot')
