from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FloatField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange


class FeeStructureForm(FlaskForm):
    title = StringField('Fee Title (e.g. Regular Academic Fee 2025-26)', validators=[DataRequired()])
    course_id = SelectField('Course / Program', coerce=int, validators=[DataRequired()])
    semester_id = SelectField('Semester', coerce=int, validators=[DataRequired()])
    session_id = SelectField('Academic Session', coerce=int, validators=[DataRequired()])
    
    tuition_fee = FloatField('Tuition Fee (₹)', default=0.0, validators=[DataRequired(), NumberRange(min=0)])
    exam_fee = FloatField('Examination Fee (₹)', default=0.0, validators=[DataRequired(), NumberRange(min=0)])
    library_fee = FloatField('Library Fee (₹)', default=0.0, validators=[DataRequired(), NumberRange(min=0)])
    lab_fee = FloatField('Laboratory / Practical Fee (₹)', default=0.0, validators=[DataRequired(), NumberRange(min=0)])
    other_fee = FloatField('Development / Other Fee (₹)', default=0.0, validators=[DataRequired(), NumberRange(min=0)])
    
    due_date = DateField('Payment Due Date', validators=[DataRequired()])
    submit = SubmitField('Create Fee Structure')


class FeePaymentForm(FlaskForm):
    amount = FloatField('Payment Amount (₹)', validators=[DataRequired(), NumberRange(min=1)])
    payment_mode = SelectField('Payment Method', choices=[
        ('Online', 'Online Banking / Card'),
        ('UPI', 'UPI (Google Pay / PhonePe / Paytm)'),
        ('Cash', 'Cash at Accounts Counter'),
        ('Cheque', 'Cheque'),
        ('Demand Draft', 'Demand Draft (DD)')
    ], default='UPI')
    transaction_id = StringField('Transaction / Reference ID', validators=[Optional()])
    notes = TextAreaField('Payment Remarks', validators=[Optional()])
    submit = SubmitField('Record Fee Payment')
