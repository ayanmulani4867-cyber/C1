from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.utils.decorators import role_required
from app.utils.uploads import save_uploaded_file
from app.models.user import Role
from app.models.student import Student
from app.models.event import Event, EventRegistration
from app.forms.event_forms import EventCreateForm

event_bp = Blueprint('event', __name__)


@event_bp.route('/')
def index():
    now = datetime.utcnow()
    upcoming_events = Event.query.filter(Event.end_datetime >= now).order_by(Event.start_datetime.asc()).all()
    past_events = Event.query.filter(Event.end_datetime < now).order_by(Event.start_datetime.desc()).limit(10).all()

    user_registered_event_ids = set()
    if current_user.is_authenticated and current_user.role == Role.STUDENT:
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student:
            regs = EventRegistration.query.filter_by(student_id=student.id, status='Confirmed').all()
            user_registered_event_ids = {r.event_id for r in regs}

    return render_template('events/index.html',
        upcoming_events=upcoming_events,
        past_events=past_events,
        user_registered_event_ids=user_registered_event_ids
    )


@event_bp.route('/<int:event_id>')
def detail(event_id):
    event = Event.query.get_or_404(event_id)
    is_registered = False
    student = None

    if current_user.is_authenticated and current_user.role == Role.STUDENT:
        student = Student.query.filter_by(user_id=current_user.id).first()
        if student:
            reg = EventRegistration.query.filter_by(event_id=event.id, student_id=student.id, status='Confirmed').first()
            is_registered = reg is not None

    registrations = []
    if current_user.is_authenticated and current_user.role in (Role.ADMIN, Role.HOD, Role.FACULTY):
        registrations = EventRegistration.query.filter_by(event_id=event.id).all()

    return render_template('events/detail.html',
        event=event,
        is_registered=is_registered,
        registrations=registrations,
        student=student
    )


@event_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required(Role.ADMIN, Role.HOD, Role.FACULTY)
def create():
    form = EventCreateForm()
    if form.validate_on_submit():
        if form.end_datetime.data <= form.start_datetime.data:
            flash('Event end time must be after the start time.', 'danger')
            return render_template('events/create.html', form=form)

        banner_filename = None
        if form.banner_image.data:
            banner_filename = save_uploaded_file(form.banner_image.data, subfolder='photos', is_image=True)

        event = Event(
            title=form.title.data.strip(),
            event_type=form.event_type.data,
            venue=form.venue.data.strip(),
            description=form.description.data.strip(),
            start_datetime=form.start_datetime.data,
            end_datetime=form.end_datetime.data,
            registration_deadline=form.registration_deadline.data,
            max_participants=form.max_participants.data or 0,
            is_open_for_registration=form.is_open_for_registration.data,
            banner_image=banner_filename,
            created_by_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()

        flash(f'Event "{event.title}" published successfully.', 'success')
        return redirect(url_for('event.detail', event_id=event.id))

    return render_template('events/create.html', form=form)


@event_bp.route('/<int:event_id>/register', methods=['POST'])
@login_required
@role_required(Role.STUDENT)
def register(event_id):
    event = Event.query.get_or_404(event_id)
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('Student record not found.', 'danger')
        return redirect(url_for('event.detail', event_id=event.id))

    if not event.is_open_for_registration:
        flash('Registration for this event is closed.', 'warning')
        return redirect(url_for('event.detail', event_id=event.id))

    if event.registration_deadline and datetime.utcnow() > event.registration_deadline:
        flash('The registration deadline for this event has passed.', 'warning')
        return redirect(url_for('event.detail', event_id=event.id))

    if event.max_participants > 0 and event.registered_count >= event.max_participants:
        flash('This event has reached maximum capacity.', 'warning')
        return redirect(url_for('event.detail', event_id=event.id))

    existing_reg = EventRegistration.query.filter_by(event_id=event.id, student_id=student.id).first()
    if existing_reg:
        if existing_reg.status == 'Confirmed':
            flash('You are already registered for this event.', 'info')
        else:
            existing_reg.status = 'Confirmed'
            existing_reg.registration_date = datetime.utcnow()
            db.session.commit()
            flash(f'Your registration for "{event.title}" has been confirmed!', 'success')
    else:
        new_reg = EventRegistration(
            event_id=event.id,
            student_id=student.id,
            status='Confirmed'
        )
        db.session.add(new_reg)
        db.session.commit()
        flash(f'Successfully registered for "{event.title}"!', 'success')

    return redirect(url_for('event.detail', event_id=event.id))


@event_bp.route('/<int:event_id>/cancel-registration', methods=['POST'])
@login_required
@role_required(Role.STUDENT)
def cancel_registration(event_id):
    event = Event.query.get_or_404(event_id)
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return redirect(url_for('event.detail', event_id=event.id))

    reg = EventRegistration.query.filter_by(event_id=event.id, student_id=student.id).first()
    if reg:
        reg.status = 'Cancelled'
        db.session.commit()
        flash(f'Your registration for "{event.title}" has been cancelled.', 'info')

    return redirect(url_for('event.detail', event_id=event.id))
