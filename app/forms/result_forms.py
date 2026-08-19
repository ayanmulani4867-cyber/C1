from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired


class ResultFilterForm(FlaskForm):
    exam_id = SelectField('Select Examination', coerce=int, validators=[DataRequired()])
    class_division_id = SelectField('Select Class Division', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Load Student Marks Roster')
