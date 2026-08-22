import io
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from datetime import date, datetime
from app.extensions import db
from app.utils.decorators import role_required, admin_required
from app.utils.pdf import generate_fee_receipt_pdf
from app.utils.helpers import generate_receipt_number, generate_transaction_id
from app.models.user import Role
from app.models.student import Student
from app.models.course import Course
from app.models.academic import Semester, AcademicSession
from app.models.fee import FeeStructure, StudentFeeRecord, FeePayment
from app.forms.fee_forms import FeeStructureForm, FeePaymentForm

fee_bp = Blueprint('fee', __name__)


@fee_bp.route('/')
@login_required
def index():
    if current_user.role == Role.STUDENT:
        std = Student.query.filter_by(user_id=current_user.id).first()
        if not std:
            flash('Student record not found.', 'warning')
            return redirect(url_for('student.dashboard'))

        fee_records = StudentFeeRecord.query.filter_by(student_id=std.id).all()
        payments = FeePayment.query.filter_by(student_id=std.id).order_by(FeePayment.payment_date.desc()).all()
        total_due = sum(r.due_amount for r in fee_records)
        total_paid = sum(r.paid_amount for r in fee_records)

        return render_template('fees/student_fees.html',
            student=std,
            fee_records=fee_records,
            payments=payments,
            total_due=total_due,
            total_paid=total_paid
        )

    # Admin view
    fee_structures = FeeStructure.query.order_by(FeeStructure.created_at.desc()).all()
    recent_payments = FeePayment.query.order_by(FeePayment.payment_date.desc()).limit(10).all()
    fee_records = StudentFeeRecord.query.all()
    total_demanded = sum(r.total_amount for r in fee_records)
    total_collected = sum(r.paid_amount for r in fee_records)
    total_pending = sum(r.due_amount for r in fee_records)

    return render_template('fees/index.html',
        fee_structures=fee_structures,
        recent_payments=recent_payments,
        total_demanded=total_demanded,
        total_collected=total_collected,
        total_pending=total_pending
    )


@fee_bp.route('/structures')
@login_required
def structures():
    return redirect(url_for('fee.index'))


@fee_bp.route('/payments')
@login_required
def payments():
    return redirect(url_for('fee.index'))


@fee_bp.route('/structures/create', methods=['GET', 'POST'])
@login_required
@admin_required
def structure_create():
    form = FeeStructureForm()
    form.course_id.choices = [(c.id, c.name) for c in Course.query.filter_by(is_active=True).all()]
    form.semester_id.choices = [(s.id, s.name) for s in Semester.query.filter_by(is_active=True).order_by(Semester.number.asc()).all()]
    form.session_id.choices = [(ses.id, ses.name) for ses in AcademicSession.query.all()]

    if form.validate_on_submit():
        total = (form.tuition_fee.data + form.exam_fee.data + form.library_fee.data +
                 form.lab_fee.data + form.other_fee.data)

        fee_struct = FeeStructure(
            title=form.title.data.strip(),
            course_id=form.course_id.data,
            semester_id=form.semester_id.data,
            session_id=form.session_id.data,
            tuition_fee=form.tuition_fee.data,
            exam_fee=form.exam_fee.data,
            library_fee=form.library_fee.data,
            lab_fee=form.lab_fee.data,
            other_fee=form.other_fee.data,
            total_amount=total,
            due_date=form.due_date.data
        )
        db.session.add(fee_struct)
        db.session.flush()

        # Generate student fee records for all active students in this course + semester
        students = Student.query.filter_by(
            course_id=form.course_id.data,
            semester_id=form.semester_id.data,
            status='Active'
        ).all()

        for std in students:
            existing = StudentFeeRecord.query.filter_by(fee_structure_id=fee_struct.id, student_id=std.id).first()
            if not existing:
                rec = StudentFeeRecord(
                    student_id=std.id,
                    fee_structure_id=fee_struct.id,
                    total_amount=total,
                    paid_amount=0.0,
                    due_amount=total,
                    status='Unpaid'
                )
                db.session.add(rec)

        db.session.commit()
        flash(f'Fee Structure "{fee_struct.title}" created and applied to {len(students)} enrolled students.', 'success')
        return redirect(url_for('fee.index'))

    return render_template('fees/structure_form.html', form=form)


@fee_bp.route('/record-payment/<int:fee_record_id>', methods=['GET', 'POST'])
@fee_bp.route('/pay/<int:fee_record_id>', methods=['GET', 'POST'])
@login_required
def record_payment(fee_record_id):
    fee_record = StudentFeeRecord.query.get_or_404(fee_record_id)
    form = FeePaymentForm()

    if request.method == 'GET':
        form.amount.data = fee_record.due_amount

    # Fallback to direct form parsing if standard WTForms doesn't match
    if request.method == 'POST' and not form.validate():
        try:
            amount = float(request.form.get('amount', 0))
            if amount > 0:
                tx_id = request.form.get('transaction_reference') or request.form.get('transaction_id') or generate_transaction_id()
                receipt_num = generate_receipt_number()
                payment = FeePayment(
                    student_fee_record_id=fee_record.id,
                    student_id=fee_record.student_id,
                    receipt_number=receipt_num,
                    amount_paid=amount,
                    payment_mode=request.form.get('payment_mode', 'Cash'),
                    transaction_id=tx_id,
                    payment_date=datetime.utcnow(),
                    collected_by_id=current_user.id,
                    notes=request.form.get('remarks') or request.form.get('notes')
                )
                db.session.add(payment)
                fee_record.paid_amount += amount
                fee_record.due_amount = max(0.0, fee_record.due_amount - amount)
                fee_record.status = 'Paid' if fee_record.due_amount <= 0 else 'Partial'
                db.session.commit()
                flash(f'Fee payment recorded successfully.', 'success')
                return redirect(url_for('fee.download_receipt', payment_id=payment.id))
        except Exception:
            pass

    if form.validate_on_submit():
        amount = form.amount.data
        if amount > fee_record.due_amount:
            flash(f'Payment amount (₹{amount}) cannot exceed current due amount (₹{fee_record.due_amount}).', 'danger')
            return render_template('fees/payment_form.html', form=form, fee_record=fee_record)

        tx_id = form.transaction_id.data.strip() if form.transaction_id.data else generate_transaction_id()
        receipt_num = generate_receipt_number()

        payment = FeePayment(
            student_fee_record_id=fee_record.id,
            student_id=fee_record.student_id,
            receipt_number=receipt_num,
            amount_paid=amount,
            payment_mode=form.payment_mode.data,
            transaction_id=tx_id,
            payment_date=datetime.utcnow(),
            collected_by_id=current_user.id,
            notes=form.notes.data.strip() if form.notes.data else None
        )
        db.session.add(payment)

        # Update fee record
        fee_record.paid_amount += amount
        fee_record.due_amount -= amount
        if fee_record.due_amount <= 0:
            fee_record.status = 'Paid'
        else:
            fee_record.status = 'Partial'

        db.session.commit()
        flash(f'Fee payment of ₹{amount:,.2f} recorded successfully with Receipt #{receipt_num}.', 'success')
        return redirect(url_for('fee.download_receipt', payment_id=payment.id))

    return render_template('fees/payment_form.html', form=form, fee_record=fee_record)


@fee_bp.route('/receipt/<int:payment_id>')
@fee_bp.route('/receipt/<int:payment_id>/download')
@login_required
def download_receipt(payment_id):
    payment = FeePayment.query.get_or_404(payment_id)
    college_info = {
        'name': current_app.config.get('COLLEGE_NAME', 'Sharad Institute of Technology'),
        'short_name': current_app.config.get('COLLEGE_SHORT_NAME', 'SITCOE'),
        'address': current_app.config.get('COLLEGE_ADDRESS', 'Yadrav (Ichalkaranji), Maharashtra - 416145'),
        'phone': current_app.config.get('COLLEGE_PHONE', '+91 2322 253000'),
        'email': current_app.config.get('COLLEGE_EMAIL', 'contact@sitcoe.org.in')
    }

    pdf_buffer = generate_fee_receipt_pdf(payment, college_info=college_info)
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"Fee_Receipt_{payment.receipt_number}.pdf"
    )


@fee_bp.route('/dues')
@login_required
@admin_required
def fee_dues():
    records = StudentFeeRecord.query.filter(StudentFeeRecord.pending_amount > 0).all()
    return render_template('fees/dues.html', records=records)
