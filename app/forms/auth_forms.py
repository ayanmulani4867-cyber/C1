from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError
from app.models.user import User


class LoginForm(FlaskForm):
    identifier = StringField('Username or Email', validators=[Optional(), Length(max=120)])
    username = StringField('Username or Email', validators=[Optional()])
    login_id = StringField('Login ID', validators=[Optional()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Sign In to Campus Connect')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        # Ensure identifier, username, or login_id can be used interchangeably
        raw_val = self.identifier.data or self.username.data or self.login_id.data
        if raw_val:
            self.identifier.data = raw_val
            self.username.data = raw_val
            self.login_id.data = raw_val

    def validate_identifier(self, field):
        val = self.identifier.data or self.username.data or self.login_id.data
        if not val or not str(val).strip():
            raise ValidationError('Username, email, or ID is required.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6, message='New password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Update Password')


class ProfileUpdateForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    phone = StringField('Phone / Mobile', validators=[Optional(), Length(max=20)])
    profile_image = FileField('Profile Picture', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only!')])
    submit = SubmitField('Save Profile Changes')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Registered Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ForgotPasswordForm(ResetPasswordRequestForm):
    pass


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')


class UserCreateForm(FlaskForm):
    from wtforms import SelectField
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Initial Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('User Role', choices=[
        ('ADMIN', 'Administrator'),
        ('HOD', 'Head of Department'),
        ('FACULTY', 'Faculty Member'),
        ('STUDENT', 'Student')
    ], validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    is_active = BooleanField('Active Account', default=True)
    submit = SubmitField('Create User Account')


