import io
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from datetime import date, datetime
from app.extensions import db
from app.utils.decorators import role_required, admin_required
from app.utils.pdf import generate_admit_card_pdf, generate_marksheet_pdf
from app.models.user import Role
from app.models.student import Student
from app.models.department import Department
from app.models.course import Course
from app.models.academic import Semester, AcademicSession, ClassDivision
from app.models.subject import Subject
from app.models.exam import Exam, ExamResult
from app.forms.exam_forms import ExamForm
from app.forms.result_forms import ResultFilterForm

exam_bp = Blueprint('exam', __name__)


@exam_bp.route('/')
@login_required
def index():
    semester_id = request.args.get('semester_id', type=int)
    course_id = request.args.get('course_id', type=int)

    if current_user.role == Role.STUDENT:
        std = Student.query.filter_by(user_id=current_user.id).first()
        if std:
            semester_id = std.semester_id
            course_id = std.course_id

    query = Exam.query
    if semester_id:
        query = query.filter(Exam.semester_id == semester_id)
    if course_id:
        query = query.join(Subject, Exam.subject_id == Subject.id).filter(Subject.course_id == course_id)

    exams = query.order_by(Exam.exam_date.asc(), Exam.start_time.asc()).all()
    courses = Course.query.filter_by(is_active=True).all()
    semesters = Semester.query.filter_by(is_active=True).all()

    return render_template('exams/index.html',
        exams=exams,
        courses=courses,
        semesters=semesters,
        selected_course=course_id,
        selected_sem=semester_id
    )


@exam_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def create():
    form = ExamForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.filter_by(is_active=True).all()]
    form.course_id.choices = [(c.id, c.name) for c in Course.query.filter_by(is_active=True).all()]
    form.semester_id.choices = [(s.id, s.name) for s in Semester.query.filter_by(is_active=True).order_by(Semester.number.asc()).all()]
    form.session_id.choices = [(ses.id, ses.name) for ses in AcademicSession.query.all()]
    form.subject_id.choices = [(s.id, f"{s.name} ({s.code})") for s in Subject.query.all()]
    
    divs = ClassDivision.query.all()
    form.class_division_id.choices = [(0, '-- All Divisions --')] + [(d.id, d.name) for d in divs]

    if form.validate_on_submit():
        exam = Exam(
            name=form.name.data.strip(),
            exam_type=form.exam_type.data,
            department_id=form.department_id.data,
            course_id=form.course_id.data,
            semester_id=form.semester_id.data,
            session_id=form.session_id.data,
            subject_id=form.subject_id.data,
            class_division_id=form.class_division_id.data if form.class_division_id.data != 0 else None,
            exam_date=form.exam_date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            room_number=form.room_number.data.strip() if form.room_number.data else None,
            max_marks=form.max_marks.data,
            passing_marks=form.passing_marks.data
        )
        db.session.add(exam)
        db.session.commit()
        flash(f'Examination "{exam.name}" scheduled for {exam.exam_date}.', 'success')
        return redirect(url_for('exam.index'))

    return render_template('exams/create.html', form=form)


@exam_bp.route('/<int:exam_id>/admit-card/download')
@login_required
def download_admit_card(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    student = None
    if current_user.role == Role.STUDENT:
        student = Student.query.filter_by(user_id=current_user.id).first()
    else:
        std_id = request.args.get('student_id', type=int)
        if std_id:
            student = Student.query.get(std_id)

    if not student:
        flash('Student record not selected.', 'danger')
        return redirect(url_for('exam.index'))

    college_info = {
        'name': current_app.config.get('COLLEGE_NAME', 'Apex Institute of Technology'),
        'address': current_app.config.get('COLLEGE_ADDRESS', 'Knowledge City, Tech Campus')
    }

    pdf_buffer = generate_admit_card_pdf(exam, student, college_info=college_info)
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"AdmitCard_{student.roll_number.replace('/', '_')}_{exam.id}.pdf"
    )


# --- MARKS ENTRY & RESULTS ---
@exam_bp.route('/results')
@login_required
def results():
    if current_user.role == Role.STUDENT:
        std = Student.query.filter_by(user_id=current_user.id).first()
        if not std:
            flash('Student not found.', 'warning')
            return redirect(url_for('student.dashboard'))
        
        my_results = ExamResult.query.filter_by(student_id=std.id, is_published=True).all()
        return render_template('exams/student_results.html', student=std, results=my_results)

    # Admin / Faculty result filter
    form = ResultFilterForm()
    form.exam_id.choices = [(e.id, f"{e.name} - {e.subject.code if e.subject else ''} ({e.exam_date})") for e in Exam.query.order_by(Exam.exam_date.desc()).all()]
    form.class_division_id.choices = [(d.id, f"{d.name} ({d.course.code})") for d in ClassDivision.query.all()]

    selected_exam_id = request.args.get('exam_id', type=int)
    selected_div_id = request.args.get('class_division_id', type=int)

    exam_obj = Exam.query.get(selected_exam_id) if selected_exam_id else None
    students = Student.query.filter_by(class_division_id=selected_div_id, status='Active').order_by(Student.roll_no.asc()).all() if selected_div_id else []

    existing_results = {}
    if exam_obj and students:
        res_list = ExamResult.query.filter_by(exam_id=exam_obj.id).all()
        existing_results = {r.student_id: r for r in res_list}

    return render_template('exams/results_roster.html',
        form=form,
        exam=exam_obj,
        students=students,
        existing_results=existing_results,
        selected_exam_id=selected_exam_id,
        selected_div_id=selected_div_id
    )


@exam_bp.route('/results/save', methods=['POST'])
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def save_results():
    exam_id = int(request.form.get('exam_id'))
    division_id = int(request.form.get('class_division_id'))
    exam = Exam.query.get_or_404(exam_id)
    students = Student.query.filter_by(class_division_id=division_id, status='Active').all()

    publish = 'publish_now' in request.form

    for std in students:
        marks_str = request.form.get(f'marks_{std.id}', '')
        remarks = request.form.get(f'remarks_{std.id}', '')

        if marks_str != '':
            try:
                marks = float(marks_str)
                pct = (marks / exam.max_marks * 100) if exam.max_marks > 0 else 0
                
                # Calculate grade
                if pct >= 90:
                    grade = 'A+'
                elif pct >= 80:
                    grade = 'A'
                elif pct >= 70:
                    grade = 'B+'
                elif pct >= 60:
                    grade = 'B'
                elif pct >= 50:
                    grade = 'C'
                elif pct >= 40:
                    grade = 'P'
                else:
                    grade = 'F'

                status = 'Pass' if marks >= exam.passing_marks else 'Fail'

                rec = ExamResult.query.filter_by(exam_id=exam.id, student_id=std.id).first()
                if not rec:
                    rec = ExamResult(
                        exam_id=exam.id,
                        student_id=std.id,
                        marks_obtained=marks,
                        grade=grade,
                        status=status,
                        remarks=remarks,
                        is_published=publish,
                        published_at=datetime.utcnow() if publish else None
                    )
                    db.session.add(rec)
                else:
                    rec.marks_obtained = marks
                    rec.grade = grade
                    rec.status = status
                    rec.remarks = remarks
                    if publish:
                        rec.is_published = True
                        rec.published_at = datetime.utcnow()
            except ValueError:
                pass

    db.session.commit()
    flash(f'Examination results saved successfully {"and published" if publish else ""}.', 'success')
    return redirect(url_for('exam.results', exam_id=exam_id, class_division_id=division_id))


@exam_bp.route('/student/<int:student_id>')
@exam_bp.route('/student/<int:student_id>/results')
@login_required
def student_results(student_id):
    student = Student.query.get_or_404(student_id)
    my_results = ExamResult.query.filter_by(student_id=student.id, is_published=True).all()
    return render_template('exams/student_results.html', student=student, results=my_results)


@exam_bp.route('/student/<int:student_id>/marksheet')
@exam_bp.route('/student/<int:student_id>/marksheet/download')
@login_required
def download_marksheet(student_id):
    student = Student.query.get_or_404(student_id)
    results = ExamResult.query.filter_by(student_id=student.id, is_published=True).all()
    college_info = {
        'name': current_app.config.get('COLLEGE_NAME', 'Apex Institute of Technology'),
        'address': current_app.config.get('COLLEGE_ADDRESS', 'Knowledge City, Tech Campus')
    }

    pdf_buffer = generate_marksheet_pdf(student, results, college_info=college_info)
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"Marksheet_{student.roll_number.replace('/', '_')}.pdf"
    )
