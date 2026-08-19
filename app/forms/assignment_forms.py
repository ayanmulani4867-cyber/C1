from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DateTimeLocalField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange


class AssignmentForm(FlaskForm):
    title = StringField('Assignment Title', validators=[DataRequired()])
    description = TextAreaField('Instructions / Description', validators=[Optional()])
    class_division_id = SelectField('Class Division', coerce=int, validators=[DataRequired()])
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    due_date = DateTimeLocalField('Due Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
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
