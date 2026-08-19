from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.utils.decorators import student_required, role_required
from app.models.user import Role
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.department import Department
from app.models.course import Course
from app.models.feedback import Feedback
from app.forms.feedback_forms import FeedbackForm

feedback_bp = Blueprint('feedback', __name__)


@feedback_bp.route('/')
@feedback_bp.route('/admin', endpoint='admin_list')
@login_required
def index():
    if current_user.role == Role.STUDENT:
        std = Student.query.filter_by(user_id=current_user.id).first()
        my_feedbacks = Feedback.query.filter_by(student_id=std.id).order_by(Feedback.created_at.desc()).all() if std else []
        return render_template('feedback/student_feedbacks.html', feedbacks=my_feedbacks)

    elif current_user.role == Role.FACULTY:
        fac = Faculty.query.filter_by(user_id=current_user.id).first()
        feedbacks = Feedback.query.filter_by(faculty_id=fac.id).order_by(Feedback.created_at.desc()).all() if fac else []
        avg_rating = round(sum(f.rating for f in feedbacks) / len(feedbacks), 1) if feedbacks else 5.0
        return render_template('feedback/faculty_feedbacks.html', feedbacks=feedbacks, avg_rating=avg_rating, faculty=fac)

    # Admin view
    all_feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    faculties = Faculty.query.filter_by(status='Active').all()
    
    # Calculate ranking / summary
    fac_ratings = []
    for f in faculties:
        fb_list = Feedback.query.filter_by(faculty_id=f.id).all()
        if fb_list:
            avg = round(sum(item.rating for item in fb_list) / len(fb_list), 2)
            fac_ratings.append({'faculty': f, 'avg': avg, 'count': len(fb_list)})
    fac_ratings.sort(key=lambda x: x['avg'], reverse=True)

    return render_template('feedback/admin_feedbacks.html', feedbacks=all_feedbacks, fac_ratings=fac_ratings)


@feedback_bp.route('/submit', methods=['GET', 'POST'])
@login_required
@student_required
def submit():
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        flash('Student account not linked.', 'warning')
        return redirect(url_for('student.dashboard'))

    form = FeedbackForm()
    faculties = Faculty.query.filter_by(status='Active').all()
    form.faculty_id.choices = [(0, '-- Select Faculty (if applicable) --')] + [(f.id, f"{f.full_name} ({f.department.code if f.department else ''})") for f in faculties]
    
    courses = Course.query.filter_by(is_active=True).all()
    form.course_id.choices = [(0, '-- Select Course (if applicable) --')] + [(c.id, c.name) for c in courses]

    depts = Department.query.filter_by(is_active=True).all()
    form.department_id.choices = [(0, '-- Select Department (if applicable) --')] + [(d.id, d.name) for d in depts]

    if form.validate_on_submit():
        feedback = Feedback(
            student_id=student.id if not form.is_anonymous.data else None,
            feedback_type=form.feedback_type.data,
            faculty_id=form.faculty_id.data if form.faculty_id.data != 0 else None,
            course_id=form.course_id.data if form.course_id.data != 0 else None,
            department_id=form.department_id.data if form.department_id.data != 0 else None,
            rating=int(form.rating.data),
            clarity_rating=int(form.clarity_rating.data),
            punctuality_rating=int(form.punctuality_rating.data),
            helpfulness_rating=int(form.helpfulness_rating.data),
            comments=form.comments.data.strip(),
            is_anonymous=form.is_anonymous.data
        )
        db.session.add(feedback)
        db.session.commit()
        flash('Thank you! Your constructive feedback has been recorded.', 'success')
        return redirect(url_for('feedback.index'))

    return render_template('feedback/submit.html', form=form)
