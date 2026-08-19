from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class ComplaintSubmitForm(FlaskForm):
    category = SelectField('Category', choices=[
        ('Academic', 'Academic (Classes / Faculty / Curriculum)'),
        ('Hostel', 'Hostel & Mess Facilities'),
        ('Infrastructure', 'Campus Infrastructure & Labs'),
        ('Ragging', 'Anti-Ragging / Harassment (Urgent)'),
        ('Fee', 'Accounts & Fee Issues'),
        ('General', 'General Grievance')
    ], validators=[DataRequired()])
    
    title = StringField('Complaint Subject / Title', validators=[DataRequired(), Length(min=5, max=150)])
    description = TextAreaField('Detailed Description', validators=[DataRequired(), Length(min=10)])
    location = StringField('Specific Location / Room / Block', validators=[Optional(), Length(max=100)])
    
    priority = SelectField('Priority Level', choices=[
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent / Immediate Action Required')
    ], default='Medium')
    
    attachment = FileField('Attach Supporting Photo / Document (Optional)', validators=[
        Optional(),
        FileAllowed(['pdf', 'jpg', 'jpeg', 'png', 'webp'], 'Allowed: PDF and Images')
    ])
    
    submit = SubmitField('Submit Grievance Ticket')


class ComplaintReviewForm(FlaskForm):
    status = SelectField('Ticket Status', choices=[
        ('Submitted', 'Submitted / Under Initial Review'),
        ('Assigned', 'Assigned to Officer'),
        ('In Progress', 'In Progress / Investigation'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed')
    ], validators=[DataRequired()])
    
    priority = SelectField('Priority Level', choices=[
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Urgent', 'Urgent')
    ])
    
    resolution_notes = TextAreaField('Administrative Resolution Notes / Action Taken', validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Update Ticket Status')
