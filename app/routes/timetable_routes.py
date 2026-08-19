from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.utils.decorators import role_required, admin_required
from app.models.user import Role
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.subject import Subject
from app.models.academic import ClassDivision, Semester, AcademicSession
from app.models.timetable import Timetable
from app.forms.timetable_forms import TimetableForm

timetable_bp = Blueprint('timetable', __name__)

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


@timetable_bp.route('/')
@login_required
def index():
    division_id = request.args.get('division_id', type=int)
    faculty_id = request.args.get('faculty_id', type=int)

    if current_user.role == Role.STUDENT and not division_id:
        std = Student.query.filter_by(user_id=current_user.id).first()
        if std and std.class_division_id:
            division_id = std.class_division_id

    if current_user.role == Role.FACULTY and not faculty_id and not division_id:
        fac = Faculty.query.filter_by(user_id=current_user.id).first()
        if fac:
            faculty_id = fac.id

    query = Timetable.query
    if division_id:
        query = query.filter_by(class_division_id=division_id)
    if faculty_id:
        query = query.filter_by(faculty_id=faculty_id)

    slots = query.order_by(Timetable.start_time.asc()).all()

    # Organize slots by Day
    timetable_grid = {day: [] for day in DAYS}
    for slot in slots:
        if slot.day_of_week in timetable_grid:
            timetable_grid[slot.day_of_week].append(slot)

    divisions = ClassDivision.query.all()
    faculties = Faculty.query.filter_by(status='Active').all()

    return render_template('timetable/index.html',
        timetable_grid=timetable_grid,
        days=DAYS,
        divisions=divisions,
        faculties=faculties,
        selected_div=division_id,
        selected_fac=faculty_id
    )


@timetable_bp.route('/manage')
@login_required
def manage():
    return redirect(url_for('timetable.index'))


@timetable_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def create():
    form = TimetableForm()
    form.class_division_id.choices = [(d.id, f"{d.name} ({d.course.code} - Sem {d.semester.number})") for d in ClassDivision.query.all()]
    form.subject_id.choices = [(s.id, f"{s.name} ({s.code})") for s in Subject.query.all()]
    form.faculty_id.choices = [(f.id, f"{f.full_name} ({f.department.code if f.department else ''})") for f in Faculty.query.filter_by(status='Active').all()]
    form.semester_id.choices = [(s.id, s.name) for s in Semester.query.filter_by(is_active=True).order_by(Semester.number.asc()).all()]
    form.session_id.choices = [(ses.id, ses.name) for ses in AcademicSession.query.all()]

    if form.validate_on_submit():
        # Check conflict
        conflict = Timetable.query.filter(
            Timetable.day_of_week == form.day_of_week.data,
            Timetable.faculty_id == form.faculty_id.data,
            Timetable.start_time == form.start_time.data
        ).first()

        if conflict:
            flash(f'Warning: Faculty {conflict.faculty.full_name} is already assigned to {conflict.class_division.name} at {form.start_time.data.strftime("%I:%M %p")}.', 'danger')
            return render_template('timetable/form.html', form=form, title='Add Timetable Slot')

        slot = Timetable(
            day_of_week=form.day_of_week.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            class_division_id=form.class_division_id.data,
            subject_id=form.subject_id.data,
            faculty_id=form.faculty_id.data,
            semester_id=form.semester_id.data,
            session_id=form.session_id.data,
            room_number=form.room_number.data.strip()
        )
        db.session.add(slot)
        db.session.commit()
        flash('Timetable slot added successfully.', 'success')
        return redirect(url_for('timetable.index', division_id=slot.class_division_id))

    return render_template('timetable/form.html', form=form, title='Add Timetable Slot')


@timetable_bp.route('/<int:slot_id>/delete', methods=['POST'])
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def delete(slot_id):
    slot = Timetable.query.get_or_404(slot_id)
    div_id = slot.class_division_id
    db.session.delete(slot)
    db.session.commit()
    flash('Timetable slot deleted.', 'info')
    return redirect(url_for('timetable.index', division_id=div_id))
