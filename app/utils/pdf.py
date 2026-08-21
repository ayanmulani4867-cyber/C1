import io
import os
import qrcode
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from flask import current_app


def generate_fee_receipt_pdf(payment, college_info=None, *args, **kwargs):
    """Generates a professional PDF receipt for a fee payment"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ReceiptTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'ReceiptSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=15
    )
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#111827')
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#374151')
    )
    
    elements = []
    
    # College Header
    elements.append(Paragraph(current_app.config.get('COLLEGE_NAME', 'Apex Institute of Technology & Science'), title_style))
    elements.append(Paragraph(f"{current_app.config.get('COLLEGE_ADDRESS', '')} | Tel: {current_app.config.get('COLLEGE_PHONE', '')}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceBefore=5, spaceAfter=15))
    
    # Receipt Banner
    receipt_banner = Paragraph("<font color='#1E3A8A'><b>FEE PAYMENT RECEIPT</b></font>", ParagraphStyle('Banner', alignment=TA_CENTER, fontSize=14))
    elements.append(receipt_banner)
    elements.append(Spacer(1, 15))
    
    student = payment.student_fee.student
    
    info_data = [
        [Paragraph(f"<b>Receipt No:</b> {payment.receipt_number}", body_style), Paragraph(f"<b>Date:</b> {payment.payment_date.strftime('%d-%b-%Y %I:%M %p')}", body_style)],
        [Paragraph(f"<b>Student Name:</b> {student.full_name}", body_style), Paragraph(f"<b>Student ID:</b> {student.student_id}", body_style)],
        [Paragraph(f"<b>Enrollment No:</b> {student.enrollment_no}", body_style), Paragraph(f"<b>Roll No:</b> {student.roll_no or 'N/A'}", body_style)],
        [Paragraph(f"<b>Department:</b> {student.department.name if student.department else 'N/A'}", body_style), Paragraph(f"<b>Course:</b> {student.course.name if student.course else 'N/A'}", body_style)],
        [Paragraph(f"<b>Semester:</b> {student.semester.name if student.semester else 'N/A'}", body_style), Paragraph(f"<b>Academic Session:</b> {student.session.name if student.session else 'N/A'}", body_style)],
    ]
    
    info_table = Table(info_data, colWidths=[260, 260])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Payment Breakdown Table
    fee_struct = payment.student_fee.fee_structure
    payment_data = [
        ['Fee Particulars', 'Amount (INR)'],
        ['Tuition Fee', f"₹ {fee_struct.tuition_fee:,.2f}"],
        ['Examination Fee', f"₹ {fee_struct.exam_fee:,.2f}"],
        ['Library Fee', f"₹ {fee_struct.library_fee:,.2f}"],
        ['Laboratory Fee', f"₹ {fee_struct.lab_fee:,.2f}"],
        ['Other Amenities', f"₹ {fee_struct.other_fee:,.2f}"],
        ['Total Course Fee', f"₹ {payment.student_fee.total_amount:,.2f}"],
        ['Discount / Scholarship', f"- ₹ {payment.student_fee.discount_amount:,.2f}"],
        ['Net Payable', f"₹ {payment.student_fee.net_payable:,.2f}"],
        ['<b>Amount Paid in this Transaction</b>', f"<b>₹ {payment.amount:,.2f}</b>"],
        ['Total Amount Paid Till Date', f"₹ {payment.student_fee.paid_amount:,.2f}"],
        ['Balance Due', f"₹ {payment.student_fee.pending_amount:,.2f}"],
    ]
    
    p_table = Table(payment_data, colWidths=[360, 160])
    p_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0,9), (1,9), colors.HexColor('#DCFCE7')),
        ('TEXTCOLOR', (0,9), (1,9), colors.HexColor('#166534')),
    ]))
    elements.append(p_table)
    elements.append(Spacer(1, 15))
    
    # Transaction Metadata
    meta_text = f"<b>Payment Mode:</b> {payment.payment_mode} | <b>Transaction ID:</b> {payment.transaction_id or 'N/A'} | <b>Status:</b> {payment.status}"
    elements.append(Paragraph(meta_text, body_style))
    elements.append(Spacer(1, 40))
    
    # Signatures
    sig_data = [
        [Paragraph("Student Signature", ParagraphStyle('sig1', alignment=TA_CENTER, fontName='Helvetica-Oblique', fontSize=9)),
         Paragraph("Authorized Accounts Officer", ParagraphStyle('sig2', alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=10))]
    ]
    sig_table = Table(sig_data, colWidths=[260, 260])
    elements.append(sig_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_marksheet_pdf(student, semester_or_results=None, results=None, college_info=None):
    """Generates official academic marksheet / grade card PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    college_name = (college_info.get('name') if college_info else None) or current_app.config.get('COLLEGE_NAME', 'Apex Institute of Technology & Science')
    college_address = (college_info.get('address') if college_info else None) or current_app.config.get('COLLEGE_ADDRESS', 'Knowledge City, Tech Campus')

    title_style = ParagraphStyle(
        'MarksheetTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=2
    )
    sub_style = ParagraphStyle(
        'SubStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=10
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#1F2937')
    )
    
    elements = []
    
    # Header
    elements.append(Paragraph(college_name, title_style))
    elements.append(Paragraph(f"{college_address} | Affiliated to State University", sub_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceBefore=2, spaceAfter=10))
    
    semester_name = student.semester.name if student.semester else 'Current Term'
    if hasattr(semester_or_results, 'name'):
        semester_name = semester_or_results.name

    elements.append(Paragraph(f"<b>OFFICIAL GRADE REPORT — {semester_name.upper()}</b>", ParagraphStyle('H2', alignment=TA_CENTER, fontSize=13, textColor=colors.HexColor('#1E3A8A'))))
    elements.append(Spacer(1, 10))
    
    # Student Info Grid
    info_data = [
        [Paragraph(f"<b>Student Name:</b> {student.full_name}", body_style), Paragraph(f"<b>Student ID:</b> {student.student_id}", body_style)],
        [Paragraph(f"<b>Enrollment No:</b> {student.enrollment_no}", body_style), Paragraph(f"<b>Roll No:</b> {student.roll_no or student.roll_number or 'N/A'}", body_style)],
        [Paragraph(f"<b>Department:</b> {student.department.name if student.department else 'N/A'}", body_style), Paragraph(f"<b>Course:</b> {student.course.name if student.course else 'N/A'}", body_style)],
        [Paragraph(f"<b>Academic Session:</b> {student.session.name if student.session else 'N/A'}", body_style), Paragraph(f"<b>Issue Date:</b> {datetime.utcnow().strftime('%d-%b-%Y')}", body_style)],
    ]
    info_table = Table(info_data, colWidths=[260, 260])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))
    
    # Results Table
    if isinstance(semester_or_results, list):
        res_list = semester_or_results
    elif results is not None:
        res_list = results
    else:
        from app.models.exam import ExamResult
        sem_id = semester_or_results.id if semester_or_results else student.semester_id
        res_list = ExamResult.query.filter_by(
            student_id=student.id,
            semester_id=sem_id
        ).all()
    
    table_data = [
        ['Code', 'Subject Name', 'Type', 'Credits', 'Max Marks', 'Obtained', 'Grade', 'Grade Pt', 'Status']
    ]
    
    total_credits = 0
    total_credit_points = 0.0
    total_obtained = 0.0
    total_max = 0.0
    
    for r in res_list:
        sub = r.subject if hasattr(r, 'subject') else (r.exam.subject if hasattr(r, 'exam') and r.exam else None)
        credits = sub.credits if sub and hasattr(sub, 'credits') else 3
        grade_pt = getattr(r, 'grade_point', 0.0)
        marks_obtained = getattr(r, 'marks_obtained', 0.0)
        max_marks = getattr(r, 'max_marks', (r.exam.max_marks if hasattr(r, 'exam') and r.exam else 100))
        grade = getattr(r, 'grade', 'P')
        status = getattr(r, 'status', 'Pass')
        
        total_credits += credits
        total_credit_points += (grade_pt * credits)
        total_obtained += marks_obtained
        total_max += max_marks
        
        table_data.append([
            sub.code if sub and hasattr(sub, 'code') else '-',
            sub.name if sub and hasattr(sub, 'name') else 'Subject',
            getattr(sub, 'subject_type', 'Theory'),
            str(credits),
            f"{max_marks:.0f}",
            f"{marks_obtained:.1f}",
            grade,
            f"{grade_pt:.1f}",
            str(status).upper()
        ])
        
    if not res_list:
        table_data.append(['No published results found for this term.', '', '', '', '', '', '', '', ''])
        
    res_table = Table(table_data, colWidths=[55, 170, 45, 40, 45, 45, 40, 45, 40])
    res_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (3,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(res_table)
    elements.append(Spacer(1, 15))
    
    # Performance Summary Box
    sgpa = round(total_credit_points / total_credits, 2) if total_credits > 0 else 0.0
    overall_pct = round((total_obtained / total_max) * 100, 2) if total_max > 0 else 0.0
    
    summary_data = [
        [f"Total Credits: {total_credits}", f"Total Marks: {total_obtained:.1f} / {total_max:.1f}", f"Percentage: {overall_pct:.2f}%", f"SGPA: {sgpa:.2f}"]
    ]
    summary_table = Table(summary_data, colWidths=[130, 130, 130, 130])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EFF6FF')),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor('#1E3A8A')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('PADDING', (0,0), (-1,-1), 6),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#93C5FD')),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 40))
    
    # Signature Footer
    sig_data = [
        [Paragraph("Verified By (HOD)", ParagraphStyle('sig1', alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=9)),
         Paragraph("Controller of Examinations", ParagraphStyle('sig2', alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=9)),
         Paragraph("Principal / Dean", ParagraphStyle('sig3', alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=9))]
    ]
    sig_table = Table(sig_data, colWidths=[173, 173, 173])
    elements.append(sig_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_id_card_pdf(student, college_info=None):
    """Generates official Student ID Card in landscape/portrait ID card size"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    college_name = (college_info.get('name') if college_info else None) or current_app.config.get('COLLEGE_NAME', 'Apex Institute of Technology & Science')
    college_address = (college_info.get('address') if college_info else None) or current_app.config.get('COLLEGE_ADDRESS', 'Knowledge City, Tech Campus')
    
    elements = []
    
    title_style = ParagraphStyle('IDTitle', fontName='Helvetica-Bold', fontSize=14, alignment=TA_CENTER, textColor=colors.HexColor('#1E3A8A'))
    sub_style = ParagraphStyle('IDSub', fontName='Helvetica', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#4B5563'))
    tag_style = ParagraphStyle('IDTag', fontName='Helvetica-Bold', fontSize=10, alignment=TA_CENTER, textColor=colors.white)
    card_body = ParagraphStyle('IDBody', fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor('#1F2937'))
    
    # Header box
    header_content = [
        [Paragraph(f"<b>{college_name}</b>", title_style)],
        [Paragraph(college_address, sub_style)],
    ]
    header_table = Table(header_content, colWidths=[360])
    
    # Generate student QR code
    qr = qrcode.QRCode(box_size=3, border=1)
    qr.add_data(f"STUDENT:{student.student_id}|ENROLL:{student.enrollment_no}|NAME:{student.full_name}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_reportlab = RLImage(qr_buffer, width=1.1*inch, height=1.1*inch)
    
    student_details = [
        [Paragraph(f"<b>Name:</b> {student.full_name}", card_body)],
        [Paragraph(f"<b>Student ID:</b> {student.student_id}", card_body)],
        [Paragraph(f"<b>Roll No:</b> {student.roll_no or student.roll_number or 'N/A'}", card_body)],
        [Paragraph(f"<b>Course:</b> {student.course.name if student.course else 'N/A'}", card_body)],
        [Paragraph(f"<b>Department:</b> {student.department.name if student.department else 'N/A'}", card_body)],
        [Paragraph(f"<b>Blood Group:</b> {student.blood_group or 'N/A'}", card_body)],
        [Paragraph(f"<b>Emergency Contact:</b> {student.emergency_phone or student.mobile or 'N/A'}", card_body)],
    ]
    std_info_table = Table(student_details, colWidths=[240])
    
    card_table_content = [
        [header_table, ''],
        [Paragraph("<b>STUDENT IDENTITY CARD</b>", tag_style), ''],
        [std_info_table, qr_reportlab],
        [Paragraph("This card is non-transferable and must be presented on demand.", ParagraphStyle('discl', fontName='Helvetica-Oblique', fontSize=7, alignment=TA_CENTER, textColor=colors.HexColor('#64748B'))), '']
    ]
    
    card_table = Table(card_table_content, colWidths=[250, 110])
    card_table.setStyle(TableStyle([
        ('SPAN', (0,0), (1,0)),
        ('SPAN', (0,1), (1,1)),
        ('SPAN', (0,3), (1,3)),
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0,1), (1,1), colors.HexColor('#1E3A8A')),
        ('BACKGROUND', (0,2), (1,-1), colors.white),
        ('ALIGN', (0,1), (1,1), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#1E3A8A')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,2), (1,2), 'MIDDLE'),
    ]))
    
    elements.append(card_table)
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_admit_card_pdf(student, exams=None, college_info=None):
    """Generates official Examination Hall Ticket / Admit Card"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    college_name = (college_info.get('name') if college_info else None) or current_app.config.get('COLLEGE_NAME', 'Apex Institute of Technology & Science')
    college_address = (college_info.get('address') if college_info else None) or current_app.config.get('COLLEGE_ADDRESS', 'Knowledge City, Tech Campus')

    elements = []
    
    title_style = ParagraphStyle('AdmitTitle', fontName='Helvetica-Bold', fontSize=16, alignment=TA_CENTER, textColor=colors.HexColor('#1E3A8A'), spaceAfter=2)
    sub_style = ParagraphStyle('AdmitSub', fontName='Helvetica', fontSize=9, alignment=TA_CENTER, textColor=colors.HexColor('#4B5563'), spaceAfter=8)
    body_style = ParagraphStyle('AdmitBody', fontName='Helvetica', fontSize=9, textColor=colors.HexColor('#1F2937'))
    
    elements.append(Paragraph(college_name, title_style))
    elements.append(Paragraph(f"{college_address} | Examination Cell", sub_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceBefore=2, spaceAfter=10))
    elements.append(Paragraph("<b>HALL TICKET / EXAMINATION ADMIT CARD</b>", ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=12, alignment=TA_CENTER, textColor=colors.HexColor('#1E3A8A'))))
    elements.append(Spacer(1, 10))
    
    info_data = [
        [Paragraph(f"<b>Student Name:</b> {student.full_name}", body_style), Paragraph(f"<b>Roll No:</b> {student.roll_no or student.roll_number or 'N/A'}", body_style)],
        [Paragraph(f"<b>Enrollment No:</b> {student.enrollment_no}", body_style), Paragraph(f"<b>Student ID:</b> {student.student_id}", body_style)],
        [Paragraph(f"<b>Department:</b> {student.department.name if student.department else 'N/A'}", body_style), Paragraph(f"<b>Course:</b> {student.course.name if student.course else 'N/A'}", body_style)],
        [Paragraph(f"<b>Semester:</b> {student.semester.name if student.semester else 'N/A'}", body_style), Paragraph(f"<b>Session:</b> {student.session.name if student.session else 'N/A'}", body_style)],
    ]
    info_table = Table(info_data, colWidths=[260, 260])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))
    
    if exams is None:
        from app.models.exam import Exam
        exams = Exam.query.filter_by(semester_id=student.semester_id, course_id=student.course_id).order_by(Exam.exam_date.asc()).all()
        
    table_data = [
        ['Date', 'Time', 'Subject Code', 'Subject Name', 'Room / Hall', 'Invigilator Sign']
    ]
    for ex in exams:
        sub = ex.subject if hasattr(ex, 'subject') else None
        date_str = ex.exam_date.strftime('%d-%b-%Y') if hasattr(ex, 'exam_date') and ex.exam_date else '-'
        time_str = f"{ex.start_time.strftime('%I:%M %p')} - {ex.end_time.strftime('%I:%M %p')}" if hasattr(ex, 'start_time') and ex.start_time else 'Morning Session'
        room_str = getattr(ex, 'room_number', 'Main Hall')
        table_data.append([
            date_str,
            time_str,
            sub.code if sub and hasattr(sub, 'code') else '-',
            sub.name if sub and hasattr(sub, 'name') else (ex.name if hasattr(ex, 'name') else 'Exam'),
            room_str,
            ''
        ])
        
    if not exams:
        table_data.append(['No upcoming examinations scheduled for this term.', '', '', '', '', ''])
        
    exam_table = Table(table_data, colWidths=[75, 110, 75, 150, 60, 50])
    exam_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(exam_table)
    elements.append(Spacer(1, 20))
    
    instructions = Paragraph(
        "<b>Important Instructions:</b><br/>"
        "1. Candidate must bring this Admit Card along with College ID Card to the exam hall.<br/>"
        "2. Electronic devices, smartwatches, and study materials are strictly prohibited.<br/>"
        "3. Report to the examination hall at least 15 minutes before scheduled start time.",
        ParagraphStyle('inst', fontName='Helvetica', fontSize=8, leading=11, textColor=colors.HexColor('#4B5563'))
    )
    elements.append(instructions)
    elements.append(Spacer(1, 30))
    
    sig_data = [
        [Paragraph("Candidate Signature", ParagraphStyle('s1', alignment=TA_CENTER, fontName='Helvetica-Oblique', fontSize=8)),
         Paragraph("Controller of Examinations", ParagraphStyle('s2', alignment=TA_CENTER, fontName='Helvetica-Bold', fontSize=9))]
    ]
    sig_table = Table(sig_data, colWidths=[260, 260])
    elements.append(sig_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer



def generate_certificate_pdf(cert_req, college_info=None, *args, **kwargs):
    """Generates official signed certificate with verification QR code"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CertCollege',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=4
    )
    sub_style = ParagraphStyle(
        'CertSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=15
    )
    cert_title_style = ParagraphStyle(
        'CertTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#B45309'),
        spaceAfter=20
    )
    cert_body_style = ParagraphStyle(
        'CertBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=22,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=15
    )
    
    elements = []
    
    college_name = (college_info.get('name') if college_info else None) or current_app.config.get('COLLEGE_NAME', 'Apex Institute of Technology & Science')
    college_address = (college_info.get('address') if college_info else None) or current_app.config.get('COLLEGE_ADDRESS', 'Knowledge City, Tech Campus')
    
    # College Header
    elements.append(Paragraph(college_name, title_style))
    elements.append(Paragraph(f"{college_address} | Accredited 'A++' Grade", sub_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1E3A8A'), spaceBefore=2, spaceAfter=15))
    
    cert_num = cert_req.certificate_number or f"CERT-{cert_req.id:05d}"
    verif_code = getattr(cert_req, 'verification_code', None) or f"V-{cert_req.id:06d}"
    issued_dt = cert_req.issued_date.strftime('%d-%b-%Y') if cert_req.issued_date else datetime.utcnow().strftime('%d-%b-%Y')
    
    # Certificate Number and Date
    ref_data = [
        [Paragraph(f"<b>Ref No:</b> {cert_num}", styles['Normal']),
         Paragraph(f"<b>Date of Issue:</b> {issued_dt}", ParagraphStyle('r', alignment=TA_RIGHT))]
    ]
    ref_table = Table(ref_data, colWidths=[260, 260])
    elements.append(ref_table)
    elements.append(Spacer(1, 20))
    
    # Certificate Type
    c_type = (cert_req.certificate_type or 'Bonafide Certificate').upper()
    elements.append(Paragraph(f"<u><b>{c_type}</b></u>", cert_title_style))
    elements.append(Spacer(1, 10))
    
    student = cert_req.student
    student_name = student.full_name if student else "Student"
    student_id = student.student_id if student else "STD-000"
    enroll_no = getattr(student, 'enrollment_no', None) or getattr(student, 'enrollment_number', None) or (student.roll_no if student else None) or student_id
    gender = getattr(student, 'gender', 'Male') if student else 'Male'
    gender_prefix = "Mr." if gender == 'Male' else ("Ms." if gender == 'Female' else "")
    pronoun = "he" if gender == 'Male' else "she"
    possessive = "his" if gender == 'Male' else "her"
    course_name = student.course.name if (student and student.course) else 'Degree Program'
    dept_name = student.department.name if (student and student.department) else 'Academic Department'
    session_name = student.session.name if (student and student.session) else '2025-26'
    purpose = cert_req.purpose or 'Institutional Records & Verification'
    
    if 'Bonafide' in c_type:
        cert_text = (
            f"This is to certify that <b>{gender_prefix} {student_name}</b>, "
            f"bearing Enrollment Number <b>{enroll_no}</b> and Student ID <b>{student_id}</b>, "
            f"is a bonafide scholar of this institution pursuing studies in <b>{course_name}</b>, "
            f"Department of <b>{dept_name}</b>, "
            f"during the academic session <b>{session_name}</b>. "
            f"<br/><br/>This certificate is officially issued upon {possessive} request for the express purpose of: <b>{purpose}</b>."
        )
    elif 'Character' in c_type:
        cert_text = (
            f"This is to certify that <b>{gender_prefix} {student_name}</b>, "
            f"bearing Enrollment Number <b>{enroll_no}</b>, has been a registered scholar of this institute in "
            f"<b>{course_name}</b>. "
            f"During {possessive} tenure of academic study at this college, {possessive} conduct and character have been found to be exemplary, disciplined, and satisfactory. "
            f"{pronoun.capitalize()} bears high moral and ethical character."
            f"<br/><br/>Issued for the purpose of: <b>{purpose}</b>."
        )
    elif 'Fee' in c_type or 'Tuition' in c_type:
        cert_text = (
            f"This is to certify that <b>{gender_prefix} {student_name}</b>, "
            f"bearing Enrollment Number <b>{enroll_no}</b> and Student ID <b>{student_id}</b>, "
            f"is enrolled in <b>{course_name}</b> (Department of {dept_name}). "
            f"All fee dues and institutional billings are reviewed under college bursar regulations."
            f"<br/><br/>Certificate issued for: <b>{purpose}</b>."
        )
    else:
        cert_text = (
            f"This is to certify that <b>{gender_prefix} {student_name}</b>, "
            f"bearing Enrollment Number <b>{enroll_no}</b> and Student ID <b>{student_id}</b>, is actively enrolled in "
            f"<b>{course_name}</b> at {college_name}. "
            f"<br/><br/>Certificate Purpose & Verification Request: <b>{purpose}</b>."
        )
        
    elements.append(Paragraph(cert_text, cert_body_style))
    elements.append(Spacer(1, 25))
    
    # Generate QR Code for verification
    qr = qrcode.QRCode(box_size=3, border=1)
    verify_data = f"CERT:{cert_num}|STUDENT:{student_id}|VERIFY:{verif_code}"
    qr.add_data(verify_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    
    qr_reportlab = RLImage(qr_buffer, width=1.1*inch, height=1.1*inch)
    
    # Footer table with QR Code and Signatures
    footer_data = [
        [qr_reportlab,
         Paragraph(f"<font size=8 color='#64748B'>Scan to verify authenticity<br/>Digital Ref: <b>{verif_code}</b></font>", styles['Normal']),
         Paragraph(f"<b>Registrar / Dean Academics</b><br/><font size=8>{college_name}</font>", ParagraphStyle('sig', alignment=TA_RIGHT, fontSize=10))]
    ]
    footer_table = Table(footer_data, colWidths=[100, 180, 240])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
    ]))
    elements.append(footer_table)
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_faculty_id_card_pdf(faculty, college_info=None):
    """Generates official Faculty Identity Card"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    college_name = (college_info.get('name') if college_info else None) or current_app.config.get('COLLEGE_NAME', 'Apex Institute of Technology & Science')
    college_address = (college_info.get('address') if college_info else None) or current_app.config.get('COLLEGE_ADDRESS', 'Knowledge City, Tech Campus')
    
    elements = []
    
    title_style = ParagraphStyle('FIDTitle', fontName='Helvetica-Bold', fontSize=14, alignment=TA_CENTER, textColor=colors.HexColor('#1E3A8A'))
    sub_style = ParagraphStyle('FIDSub', fontName='Helvetica', fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#4B5563'))
    tag_style = ParagraphStyle('FIDTag', fontName='Helvetica-Bold', fontSize=10, alignment=TA_CENTER, textColor=colors.white)
    card_body = ParagraphStyle('FIDBody', fontName='Helvetica', fontSize=9, leading=12, textColor=colors.HexColor('#1F2937'))
    
    # Header box
    header_content = [
        [Paragraph(f"<b>{college_name}</b>", title_style)],
        [Paragraph(college_address, sub_style)],
    ]
    header_table = Table(header_content, colWidths=[360])
    
    # Generate faculty QR code
    qr = qrcode.QRCode(box_size=3, border=1)
    qr.add_data(f"FACULTY:{faculty.faculty_id}|EMP:{faculty.employee_id}|NAME:{faculty.full_name}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    qr_reportlab = RLImage(qr_buffer, width=1.1*inch, height=1.1*inch)
    
    faculty_details = [
        [Paragraph(f"<b>Name:</b> {faculty.full_name}", card_body)],
        [Paragraph(f"<b>Faculty ID:</b> {faculty.faculty_id}", card_body)],
        [Paragraph(f"<b>Employee ID:</b> {faculty.employee_id}", card_body)],
        [Paragraph(f"<b>Designation:</b> {faculty.designation}", card_body)],
        [Paragraph(f"<b>Department:</b> {faculty.department.name if faculty.department else 'N/A'}", card_body)],
        [Paragraph(f"<b>Blood Group:</b> {faculty.blood_group or 'N/A'}", card_body)],
        [Paragraph(f"<b>Emergency Contact:</b> {faculty.emergency_phone or faculty.mobile or 'N/A'}", card_body)],
    ]
    fac_info_table = Table(faculty_details, colWidths=[240])
    
    card_table_content = [
        [header_table, ''],
        [Paragraph("<b>FACULTY IDENTITY CARD</b>", tag_style), ''],
        [fac_info_table, qr_reportlab],
        [Paragraph("Authorized Personnel Identification Card - Campus Connect", ParagraphStyle('discl_f', fontName='Helvetica-Oblique', fontSize=7, alignment=TA_CENTER, textColor=colors.HexColor('#64748B'))), '']
    ]
    
    card_table = Table(card_table_content, colWidths=[250, 110])
    card_table.setStyle(TableStyle([
        ('SPAN', (0,0), (1,0)),
        ('SPAN', (0,1), (1,1)),
        ('SPAN', (0,3), (1,3)),
        ('BACKGROUND', (0,0), (1,0), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0,1), (1,1), colors.HexColor('#1E3A8A')),
        ('BACKGROUND', (0,2), (1,-1), colors.white),
        ('ALIGN', (0,1), (1,1), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#1E3A8A')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,2), (1,2), 'MIDDLE'),
    ]))
    
    elements.append(card_table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

