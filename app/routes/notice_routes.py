from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import date, datetime
from app.extensions import db
from app.utils.decorators import role_required, admin_required
from app.utils.uploads import save_uploaded_file
from app.models.user import Role
from app.models.department import Department
from app.models.academic import ClassDivision
from app.models.notice import Notice
from app.forms.notice_forms import NoticeForm

notice_bp = Blueprint('notice', __name__)


@notice_bp.route('/')
def index():
    audience = request.args.get('audience', 'ALL')
    dept_id = request.args.get('dept_id', type=int)

    query = Notice.query.filter_by(is_published=True)
    if audience != 'ALL':
        query = query.filter_by(target_audience=audience)
    if dept_id:
        query = query.filter_by(department_id=dept_id)

    notices = query.order_by(Notice.created_at.desc()).all()
    departments = Department.query.filter_by(is_active=True).all()

    return render_template('notices/index.html', notices=notices, departments=departments, selected_audience=audience, selected_dept=dept_id)


@notice_bp.route('/<int:notice_id>')
def detail(notice_id):
    notice = Notice.query.get_or_404(notice_id)
    return render_template('notices/detail.html', notice=notice)


@notice_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def create():
    form = NoticeForm()
    depts = Department.query.filter_by(is_active=True).all()
    form.department_id.choices = [(0, '-- None / Institute-wide --')] + [(d.id, d.name) for d in depts]
    divs = ClassDivision.query.all()
    form.class_division_id.choices = [(0, '-- None / All Divisions --')] + [(d.id, d.name) for d in divs]

    if request.method == 'GET' and not form.publish_date.data:
        form.publish_date.data = date.today()

    if form.validate_on_submit():
        attachment_file = None
        if form.attachment_file.data:
            attachment_file = save_uploaded_file(form.attachment_file.data, subfolder='documents')

        notice = Notice(
            title=form.title.data.strip(),
            content=form.content.data.strip(),
            target_audience=form.target_audience.data,
            department_id=form.department_id.data if form.department_id.data != 0 else None,
            class_division_id=form.class_division_id.data if form.class_division_id.data != 0 else None,
            priority=form.priority.data,
            publish_date=form.publish_date.data,
            expiry_date=form.expiry_date.data,
            attachment_file=attachment_file,
            created_by_id=current_user.id,
            is_published=True
        )
        db.session.add(notice)
        db.session.commit()
        flash(f'Notice "{notice.title}" published to notice board.', 'success')
        return redirect(url_for('notice.index'))

    return render_template('notices/create.html', form=form)


@notice_bp.route('/<int:notice_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def edit(notice_id):
    notice = Notice.query.get_or_404(notice_id)
    form = NoticeForm(obj=notice)
    depts = Department.query.filter_by(is_active=True).all()
    form.department_id.choices = [(0, '-- None / Institute-wide --')] + [(d.id, d.name) for d in depts]
    divs = ClassDivision.query.all()
    form.class_division_id.choices = [(0, '-- None / All Divisions --')] + [(d.id, d.name) for d in divs]

    if request.method == 'GET':
        form.department_id.data = notice.department_id or 0
        form.class_division_id.data = notice.class_division_id or 0

    if form.validate_on_submit():
        notice.title = form.title.data.strip()
        notice.content = form.content.data.strip()
        notice.target_audience = form.target_audience.data
        notice.department_id = form.department_id.data if form.department_id.data != 0 else None
        notice.class_division_id = form.class_division_id.data if form.class_division_id.data != 0 else None
        notice.priority = form.priority.data
        notice.publish_date = form.publish_date.data
        notice.expiry_date = form.expiry_date.data
        if form.attachment_file.data:
            att = save_uploaded_file(form.attachment_file.data, subfolder='documents')
            if att:
                notice.attachment_file = att
        db.session.commit()
        flash(f'Notice "{notice.title}" updated successfully.', 'success')
        return redirect(url_for('notice.detail', notice_id=notice.id))

    return render_template('notices/create.html', form=form, title='Edit Notice', notice=notice)


@notice_bp.route('/<int:notice_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(notice_id):
    notice = Notice.query.get_or_404(notice_id)
    db.session.delete(notice)
    db.session.commit()
    flash('Notice removed.', 'info')
    return redirect(url_for('notice.index'))
