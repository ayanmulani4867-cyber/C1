from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional


class NoticeForm(FlaskForm):
    title = StringField('Circular / Notice Heading', validators=[DataRequired()])
    content = TextAreaField('Detailed Announcement Content', validators=[DataRequired()])
    target_audience = SelectField('Target Audience', choices=[
        ('ALL', 'All Campus Members (Students & Faculty)'),
        ('DEPARTMENT', 'Specific Department Only'),
        ('FACULTY', 'All Faculty Members'),
        ('STUDENT', 'All Students')
    ], default='ALL')
    department_id = SelectField('Target Department', coerce=int, validators=[Optional()])
    class_division_id = SelectField('Target Class Division (Optional)', coerce=int, validators=[Optional()])
    priority = SelectField('Priority Level', choices=[
        ('Normal', 'Normal Notice'),
        ('Important', 'Important Notice'),
        ('Urgent', 'Urgent / High Priority')
    ], default='Normal')
    publish_date = DateField('Publish Date', validators=[DataRequired()])
    expiry_date = DateField('Expiry Date (Optional)', validators=[Optional()])
    attachment_file = FileField('Circular Document / PDF (Optional)', validators=[
        Optional(),
        FileAllowed(['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'], 'Allowed: PDF, DOC, Images')
    ])
    submit = SubmitField('Publish Notice')
