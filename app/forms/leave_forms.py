from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional


class LeaveApplyForm(FlaskForm):
    leave_type = SelectField('Leave Category', choices=[
        ('Sick Leave', 'Sick Leave'),
        ('Medical Leave', 'Medical / Sickness Leave'),
        ('Casual Leave', 'Casual / Personal Leave'),
        ('Academic Duty', 'Academic / Seminar / Duty Leave'),
        ('Duty Leave', 'Duty Leave'),
        ('Emergency Leave', 'Emergency / Compassionate Leave'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    reason = TextAreaField('Reason for Leave Request', validators=[DataRequired()])
    document_file = FileField('Supporting Document / Medical Slip (Optional)', validators=[
        Optional(),
        FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 'PDF and Images only!')
    ])
    submit = SubmitField('Submit Leave Application')


class LeaveReviewForm(FlaskForm):
    status = SelectField('Decision', choices=[
        ('Approved', 'Approve Leave'),
        ('Rejected', 'Reject Leave')
    ], validators=[DataRequired()])
    review_comment = TextAreaField('Officer Remarks / Feedback', validators=[Optional()])
    submit = SubmitField('Submit Decision')
