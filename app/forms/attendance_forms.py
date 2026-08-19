from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional


class AttendanceFilterForm(FlaskForm):
    class_division_id = SelectField('Class Division', coerce=int, validators=[DataRequired()])
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    date = DateField('Attendance Date', validators=[DataRequired()])
    time_slot = StringField('Time Slot (e.g. 09:00 - 10:00 AM)', validators=[Optional()])
    topic_covered = StringField('Topic Covered', validators=[Optional()])
    submit = SubmitField('Load Student Roster')
