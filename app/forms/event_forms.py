from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, IntegerField, BooleanField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange


class EventCreateForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=150)])
    event_type = SelectField('Event Category', choices=[
        ('Academic', 'Academic & Conference'),
        ('Cultural', 'Cultural & Arts Fest'),
        ('Sports', 'Sports & Tournaments'),
        ('Workshop', 'Technical Workshop & Hands-on'),
        ('Seminar', 'Guest Seminar & Keynote'),
        ('Hackathon', 'Hackathon & Coding Contest'),
        ('Placement', 'Campus Placement & Recruitment'),
        ('Other', 'Other Campus Activity')
    ], default='Academic')
    
    venue = StringField('Venue / Location / Hall', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Event Details & Schedule', validators=[DataRequired(), Length(min=10)])
    
    start_datetime = DateTimeLocalField('Start Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_datetime = DateTimeLocalField('End Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    registration_deadline = DateTimeLocalField('Registration Deadline (Optional)', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    
    max_participants = IntegerField('Capacity Limit (0 for Unlimited)', default=0, validators=[Optional(), NumberRange(min=0)])
    is_open_for_registration = BooleanField('Open for Student Online Registration', default=True)
    
    banner_image = FileField('Event Banner Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only (jpg, jpeg, png, webp)')
    ])
    
    submit = SubmitField('Publish Campus Event')
