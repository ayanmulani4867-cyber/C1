from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import date, datetime
from app.extensions import db
from app.utils.decorators import role_required
from app.models.user import Role
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.subject import Subject
from app.models.academic import ClassDivision
from app.models.attendance import AttendanceSession, AttendanceRecord
from app.forms.attendance_forms import AttendanceFilterForm

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/')
@login_required
def index():
    if current_user.role == Role.STUDENT:
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student:
            flash('Student profile not found.', 'warning')
            return redirect(url_for('student.dashboard'))
        
        records = AttendanceRecord.query.filter_by(student_id=student.id).all()
        # Group by subject
        subject_stats = {}
        for r in records:
            s_name = r.session.subject.name if r.session and r.session.subject else 'General'
            if s_name not in subject_stats:
                subject_stats[s_name] = {'total': 0, 'present': 0, 'absent': 0, 'late': 0}
            subject_stats[s_name]['total'] += 1
            if r.status == 'Present':
                subject_stats[s_name]['present'] += 1
            elif r.status == 'Absent':
                subject_stats[s_name]['absent'] += 1
            elif r.status == 'Late':
                subject_stats[s_name]['late'] += 1

        for k, v in subject_stats.items():
            total = v['total']
            attended = v['present'] + v['late']
            v['pct'] = round((attended / total * 100), 1) if total > 0 else 0

        return render_template('attendance/student_view.html', student=student, records=records, subject_stats=subject_stats)

    # Faculty / Admin view
    divisions = ClassDivision.query.all()
    subjects = Subject.query.all()
    recent_sessions = AttendanceSession.query.order_by(AttendanceSession.date.desc(), AttendanceSession.created_at.desc()).limit(10).all()
    
    return render_template('attendance/index.html', divisions=divisions, subjects=subjects, recent_sessions=recent_sessions)


@attendance_bp.route('/mark', methods=['GET', 'POST'])
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def mark():
    form = AttendanceFilterForm()
    
    # Preload choices
    if current_user.role == Role.FACULTY:
        faculty = Faculty.query.filter_by(user_id=current_user.id).first()
        assigned_subj_ids = [s.id for s in faculty.subjects] if faculty else []
        subjects = Subject.query.filter(Subject.id.in_(assigned_subj_ids)).all() if assigned_subj_ids else Subject.query.all()
    else:
        subjects = Subject.query.all()

    form.class_division_id.choices = [(d.id, f"{d.name} ({d.course.code} - Sem {d.semester.number})") for d in ClassDivision.query.all()]
    form.subject_id.choices = [(s.id, f"{s.name} ({s.code})") for s in subjects]

    selected_div_id = request.args.get('class_division_id', type=int) or (form.class_division_id.data if request.method == 'POST' else None)
    selected_subj_id = request.args.get('subject_id', type=int) or (form.subject_id.data if request.method == 'POST' else None)
    att_date = request.args.get('date') or (form.date.data.strftime('%Y-%m-%d') if form.date.data else date.today().strftime('%Y-%m-%d'))
    time_slot = request.args.get('time_slot') or form.time_slot.data or '09:00 - 10:00 AM'

    students = []
    if selected_div_id:
        students = Student.query.filter_by(division_id=selected_div_id, status='Active').order_by(Student.roll_no.asc()).all()

    if request.method == 'POST' and 'save_attendance' in request.form:
        division_id = int(request.form.get('class_division_id'))
        subject_id = int(request.form.get('subject_id'))
        session_date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
        slot = request.form.get('time_slot', '09:00 - 10:00 AM')
        topic = request.form.get('topic_covered', '')

        faculty_id = None
        if current_user.role == Role.FACULTY:
            fac = Faculty.query.filter_by(user_id=current_user.id).first()
            if fac:
                faculty_id = fac.id

        # Create or update AttendanceSession
        att_session = AttendanceSession.query.filter_by(
            class_division_id=division_id,
            subject_id=subject_id,
            date=session_date,
            time_slot=slot
        ).first()

        if not att_session:
            att_session = AttendanceSession(
                class_division_id=division_id,
                subject_id=subject_id,
                faculty_id=faculty_id,
                date=session_date,
                time_slot=slot,
                topic_covered=topic
            )
            db.session.add(att_session)
            db.session.flush()
        else:
            att_session.topic_covered = topic
            if faculty_id:
                att_session.faculty_id = faculty_id

        # Record statuses
        for std in students:
            status = request.form.get(f'status_{std.id}', 'Present')
            remarks = request.form.get(f'remarks_{std.id}', '')

            rec = AttendanceRecord.query.filter_by(
                attendance_session_id=att_session.id,
                student_id=std.id
            ).first()

            if not rec:
                rec = AttendanceRecord(
                    attendance_session_id=att_session.id,
                    student_id=std.id,
                    status=status,
                    remarks=remarks
                )
                db.session.add(rec)
            else:
                rec.status = status
                rec.remarks = remarks

        db.session.commit()
        flash(f'Attendance recorded successfully for {len(students)} students on {session_date}.', 'success')
        return redirect(url_for('attendance.session_detail', session_id=att_session.id))

    return render_template('attendance/mark.html',
        form=form,
        students=students,
        selected_div_id=selected_div_id,
        selected_subj_id=selected_subj_id,
        att_date=att_date,
        time_slot=time_slot
    )


@attendance_bp.route('/session/<int:session_id>')
@login_required
def session_detail(session_id):
    session_obj = AttendanceSession.query.get_or_404(session_id)
    records = AttendanceRecord.query.filter_by(attendance_session_id=session_id).all()
    present_cnt = sum(1 for r in records if r.status in ('Present', 'Late'))
    total_cnt = len(records)
    pct = round((present_cnt / total_cnt * 100), 1) if total_cnt > 0 else 0

    return render_template('attendance/session_detail.html',
        session_obj=session_obj,
        records=records,
        present_cnt=present_cnt,
        total_cnt=total_cnt,
        pct=pct
    )


@attendance_bp.route('/report')
@login_required
def report():
    return redirect(url_for('report.attendance_report'))


@attendance_bp.route('/low-attendance')
@attendance_bp.route('/defaulters', endpoint='defaulters')
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def low_attendance():
    # Find students with < 75% attendance
    students = Student.query.filter_by(status='Active').all()
    low_att_students = []

    for std in students:
        records = AttendanceRecord.query.filter_by(student_id=std.id).all()
        total = len(records)
        if total >= 3:  # minimum sessions threshold
            present = sum(1 for r in records if r.status in ('Present', 'Late'))
            pct = round((present / total * 100), 1)
            if pct < 75.0:
                low_att_students.append({
                    'student': std,
                    'total': total,
                    'present': present,
                    'absent': total - present,
                    'percentage': pct
                })

    low_att_students.sort(key=lambda x: x['percentage'])
    return render_template('attendance/low_attendance.html', list=low_att_students)
