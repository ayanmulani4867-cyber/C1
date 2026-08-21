import io
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
import pandas as pd
from datetime import datetime, date
from app.extensions import db
from app.utils.decorators import role_required, admin_required
from app.models.user import Role
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.department import Department
from app.models.course import Course
from app.models.academic import ClassDivision
from app.models.attendance import AttendanceRecord, AttendanceSession
from app.models.fee import FeePayment, StudentFeeRecord

report_bp = Blueprint('report', __name__)


@report_bp.route('/')
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def index():
    departments = Department.query.filter_by(is_active=True).all()
    courses = Course.query.filter_by(is_active=True).all()
    divisions = ClassDivision.query.all()

    # Department student distribution
    dept_stats = []
    for d in departments:
        std_count = Student.query.filter_by(department_id=d.id, status='Active').count()
        fac_count = Faculty.query.filter_by(department_id=d.id, status='Active').count()
        dept_stats.append({
            'name': d.name,
            'code': d.code,
            'students': std_count,
            'faculty': fac_count
        })

    return render_template('reports/index.html',
        departments=departments,
        courses=courses,
        divisions=divisions,
        dept_stats=dept_stats
    )


@report_bp.route('/attendance')
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def attendance_report():
    return redirect(url_for('report.index'))


@report_bp.route('/results')
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def result_report():
    return redirect(url_for('report.index'))


@report_bp.route('/fees')
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def fee_report():
    return redirect(url_for('report.index'))


@report_bp.route('/students')
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def student_report():
    return redirect(url_for('report.index'))


@report_bp.route('/faculty')
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def faculty_report():
    return redirect(url_for('report.index'))


@report_bp.route('/export/students')
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def export_students():
    dept_id = request.args.get('dept_id', type=int)
    course_id = request.args.get('course_id', type=int)
    division_id = request.args.get('division_id', type=int)

    query = Student.query
    if dept_id:
        query = query.filter_by(department_id=dept_id)
    if course_id:
        query = query.filter_by(course_id=course_id)
    if division_id:
        query = query.filter_by(class_division_id=division_id)

    students = query.order_by(Student.roll_no.asc()).all()

    data = []
    for s in students:
        data.append({
            'Roll Number': s.roll_no or s.roll_number,
            'Admission Number': s.admission_no or s.admission_number,
            'Full Name': s.full_name,
            'Gender': s.gender or '',
            'Official Email': s.official_email or s.college_email,
            'Mobile': s.mobile or '',
            'Department': s.department.name if s.department else '',
            'Course': s.course.name if s.course else '',
            'Semester': s.semester.name if s.semester else '',
            'Division': s.class_division.name if s.class_division else (s.division.name if s.division else 'Unassigned'),
            'Category': s.admission_type or getattr(s, 'admission_category', '') or '',
            'Admission Date': s.admission_date.strftime('%Y-%m-%d') if s.admission_date else '',
            'Status': s.status
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Students')
    output.seek(0)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'Students_Report_{timestamp}.xlsx'
    )


@report_bp.route('/export/attendance')
@login_required
@role_required(Role.ADMIN, Role.FACULTY)
def export_attendance():
    records = AttendanceRecord.query.order_by(AttendanceRecord.id.desc()).limit(1000).all()
    data = []
    for r in records:
        student = r.student
        session = r.session
        data.append({
            'Record ID': r.id,
            'Student Roll': (student.roll_no or student.roll_number) if student else '',
            'Student Name': student.full_name if student else '',
            'Subject': session.subject.name if session and session.subject else '',
            'Date': session.date.strftime('%Y-%m-%d') if session and session.date else '',
            'Status': r.status,
            'Remarks': r.remarks or ''
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
    output.seek(0)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'Attendance_Report_{timestamp}.xlsx'
    )


@report_bp.route('/export/faculty')
@login_required
@admin_required
def export_faculty():
    faculty_list = Faculty.query.order_by(Faculty.first_name.asc()).all()
    data = []
    for f in faculty_list:
        data.append({
            'Faculty ID': f.faculty_id,
            'Employee ID': f.employee_id,
            'Full Name': f.full_name,
            'Designation': f.designation,
            'Department': f.department.name if f.department else '',
            'Employment Type': f.employment_type,
            'Official Email': f.official_email,
            'Mobile': f.mobile,
            'Qualification': f.qualification or '',
            'Specialization': f.specialization or '',
            'Experience (Years)': f.experience_years,
            'Joining Date': f.joining_date.strftime('%Y-%m-%d') if f.joining_date else '',
            'Status': f.status
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Faculty')
    output.seek(0)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'Faculty_Report_{timestamp}.xlsx'
    )


@report_bp.route('/export/fees')
@login_required
@admin_required
def export_fees():
    payments = FeePayment.query.order_by(FeePayment.payment_date.desc()).all()
    data = []
    for p in payments:
        data.append({
            'Receipt Number': p.receipt_number,
            'Payment Date': p.payment_date.strftime('%Y-%m-%d %H:%M') if p.payment_date else '',
            'Student Roll': (p.student.roll_no or p.student.roll_number) if p.student else '',
            'Student Name': p.student.full_name if p.student else '',
            'Course': p.student.course.code if p.student and p.student.course else '',
            'Amount Paid (₹)': p.amount_paid,
            'Payment Mode': p.payment_mode,
            'Transaction ID': p.transaction_id or '',
            'Remarks': p.notes or ''
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Fee Collection')
    output.seek(0)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'Fee_Collection_Report_{timestamp}.xlsx'
    )
