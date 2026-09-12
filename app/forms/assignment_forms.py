from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, Field, FloatField, SelectField, SubmitField
from wtforms.widgets import TextInput
from wtforms.validators import DataRequired, Optional, NumberRange
from datetime import datetime


class FlexibleDateTimeField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return self.data.strftime('%Y-%m-%dT%H:%M')
        return ''

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = valuelist[0].strip()
            if not date_str:
                self.data = None
                return
            formats = [
                '%Y-%m-%dT%H:%M',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%Y-%m-%d'
            ]
            for fmt in formats:
                try:
                    self.data = datetime.strptime(date_str, fmt)
                    return
                except ValueError:
                    continue
            raise ValueError(f"Invalid date/time format: {date_str}")
        else:
            self.data = None


class AssignmentForm(FlaskForm):
    title = StringField('Assignment Title', validators=[DataRequired()])
    description = TextAreaField('Instructions / Description', validators=[Optional()])
    class_division_id = SelectField('Class Division', coerce=int, validators=[DataRequired()])
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    due_date = FlexibleDateTimeField('Due Date & Time', validators=[DataRequired()])
    max_marks = FloatField('Maximum Marks', default=20.0, validators=[DataRequired(), NumberRange(min=1)])
    attachment_file = FileField('Question Paper / Attachment (Optional)', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'], 'Allowed: PDF, DOC, DOCX, Images, TXT')
    ])
    submit = SubmitField('Publish Assignment')


class AssignmentSubmissionForm(FlaskForm):
    submission_text = TextAreaField('Submission Comments / Notes', validators=[Optional()])
    submission_file = FileField('Submission Document (PDF/DOC/ZIP)', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'zip', 'jpg', 'png', 'txt'], 'Allowed: PDF, DOC, DOCX, ZIP, Images, TXT')
    ])
    submit = SubmitField('Submit Assignment')


class GradeSubmissionForm(FlaskForm):
    marks_obtained = FloatField('Marks Awarded', validators=[DataRequired(), NumberRange(min=0)])
    feedback = TextAreaField('Faculty Feedback / Remarks', validators=[Optional()])
    submit = SubmitField('Submit Grade & Feedback')


class StudyMaterialForm(FlaskForm):
    title = StringField('Material Title', validators=[DataRequired()])
    description = TextAreaField('Topic Summary / Description', validators=[Optional()])
    class_division_id = SelectField('Class Division', coerce=int, validators=[DataRequired()])
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    material_file = FileField('Upload Study Notes / Presentation', validators=[
        DataRequired(),
        FileAllowed(['pdf', 'ppt', 'pptx', 'doc', 'docx', 'txt'], 'Allowed: PDF, PPT, PPTX, DOC, DOCX, TXT')
    ])
    submit = SubmitField('Upload Study Material')
