from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional


class CertificateRequestForm(FlaskForm):
    certificate_type = SelectField('Certificate Type', choices=[
        ('Bonafide', 'Bonafide Student Certificate'),
        ('Character Certificate', 'Character & Conduct Certificate'),
        ('Fee Certificate', 'Tuition Fee / Expenditure Certificate (for Bank/Tax)'),
        ('Course Completion', 'Provisional Course Completion Certificate'),
        ('Medium of Instruction', 'English Medium of Instruction Certificate')
    ], validators=[DataRequired()])
    purpose = TextAreaField('Detailed Purpose / Organization where submitting', validators=[DataRequired()])
    submit = SubmitField('Submit Certificate Request')


class CertificateReviewForm(FlaskForm):
    status = SelectField('Action Decision', choices=[
        ('Approved', 'Approve and Issue Certificate'),
        ('Rejected', 'Reject Request')
    ], validators=[DataRequired()])
    rejection_reason = TextAreaField('Reason if rejecting', validators=[Optional()])
    submit = SubmitField('Process Certificate')
