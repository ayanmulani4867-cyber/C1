from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app.extensions import db
from app.models.user import User, Role
from app.forms.auth_forms import LoginForm, ChangePasswordForm, ProfileUpdateForm, ResetPasswordRequestForm, ResetPasswordForm
from app.utils.uploads import save_uploaded_file

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == Role.ADMIN:
            return redirect(url_for('admin.dashboard'))
        elif current_user.role in (Role.FACULTY, Role.HOD):
            return redirect(url_for('faculty.dashboard'))
        elif current_user.role == Role.STUDENT:
            return redirect(url_for('student.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_identifier(form.identifier.data.strip())
        if user and user.verify_password(form.password.data):
            if not user.is_active:
                flash('Your account is currently inactive. Please contact the administrative office.', 'danger')
                return render_template('auth/login.html', form=form)

            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()

            flash(f'Welcome back, {user.first_name or user.username}!', 'success')
            next_page = request.args.get('next')
            if next_page and not next_page.startswith('/auth/login') and not next_page.startswith('/auth/logout'):
                return redirect(next_page)

            if user.role == Role.ADMIN:
                return redirect(url_for('admin.dashboard'))
            elif user.role in (Role.FACULTY, Role.HOD):
                return redirect(url_for('faculty.dashboard'))
            elif user.role == Role.STUDENT:
                return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid username/email or password. Please check your credentials.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileUpdateForm(obj=current_user)
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data.strip()
        current_user.last_name = form.last_name.data.strip()
        current_user.phone = form.phone.data.strip() if form.phone.data else None
        
        # Profile image upload
        if form.profile_image.data:
            filename = save_uploaded_file(form.profile_image.data, subfolder='photos', is_image=True)
            if filename:
                current_user.profile_image = filename
                
        db.session.commit()
        flash('Your profile details have been updated successfully.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html', form=form, user=current_user)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.verify_password(form.old_password.data):
            flash('Your current password was entered incorrectly.', 'danger')
            return render_template('auth/change_password.html', form=form)

        current_user.set_password(form.new_password.data)
        current_user.must_change_password = False
        db.session.commit()
        flash('Your password has been changed successfully. Please keep it confidential.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/change_password.html', form=form)


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user:
            flash(f'A password reset verification link has been generated for {user.email}. (Demo mode: You can also reset password directly through Admin console).', 'info')
        else:
            flash('If an account exists with that email, reset instructions will be sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html', form=form)
