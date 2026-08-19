import io
import pandas as pd
from datetime import datetime


def export_students_to_excel(students_query):
    """Exports student list to an Excel workbook"""
    data = []
    for s in students_query:
        data.append({
            'Student ID': s.student_id,
            'Enrollment No': s.enrollment_no,
            'Admission No': s.admission_no,
            'Roll No': s.roll_no or '',
            'Full Name': s.full_name,
            'Gender': s.gender or '',
            'DOB': s.dob.strftime('%d-%m-%Y') if s.dob else '',
            'Department': s.department.name if s.department else '',
            'Course': s.course.name if s.course else '',
            'Semester': s.semester.name if s.semester else '',
            'Division': s.division.name if s.division else '',
            'College Email': s.college_email,
            'Mobile': s.mobile,
            'Status': s.status,
            'Admission Date': s.admission_date.strftime('%d-%m-%Y') if s.admission_date else ''
        })
        
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Students')
    output.seek(0)
    return output


def export_faculty_to_excel(faculty_query):
    """Exports faculty list to Excel"""
    data = []
    for f in faculty_query:
        data.append({
            'Faculty ID': f.faculty_id,
            'Employee ID': f.employee_id,
            'Full Name': f.full_name,
            'Department': f.department.name if f.department else '',
            'Designation': f.designation,
            'Employment Type': f.employment_type,
            'Official Email': f.official_email,
            'Mobile': f.mobile,
            'Qualification': f.qualification or '',
            'Experience (Years)': f.experience_years or 0,
            'Status': f.status
        })
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Faculty')
    output.seek(0)
    return output


def export_attendance_to_csv(attendance_records_query):
    """Exports attendance records to CSV"""
    data = []
    for r in attendance_records_query:
        sess = r.session
        data.append({
            'Date': sess.date.strftime('%Y-%m-%d'),
            'Time Slot': sess.time_slot or '',
            'Subject Code': sess.subject.code if sess.subject else '',
            'Subject Name': sess.subject.name if sess.subject else '',
            'Class Division': sess.class_division.display_name if sess.class_division else '',
            'Student ID': r.student.student_id if r.student else '',
            'Student Name': r.student.full_name if r.student else '',
            'Roll No': r.student.roll_no if r.student else '',
            'Status': r.status,
            'Remarks': r.remarks or ''
        })
    df = pd.DataFrame(data)
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue()
