from datetime import datetime
from app.extensions import db


class FeeStructure(db.Model):
    __tablename__ = 'fee_structures'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # e.g. "Tuition Fee Semester 4"
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id', ondelete='CASCADE'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('academic_sessions.id', ondelete='CASCADE'), nullable=False)
    
    tuition_fee = db.Column(db.Float, default=0.0, nullable=False)
    exam_fee = db.Column(db.Float, default=0.0, nullable=False)
    library_fee = db.Column(db.Float, default=0.0, nullable=False)
    lab_fee = db.Column(db.Float, default=0.0, nullable=False)
    other_fee = db.Column(db.Float, default=0.0, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def name(self):
        return self.title

    @name.setter
    def name(self, value):
        self.title = value

    @property
    def examination_fee(self):
        return self.exam_fee

    @examination_fee.setter
    def examination_fee(self, value):
        self.exam_fee = value

    @property
    def laboratory_fee(self):
        return self.lab_fee

    @laboratory_fee.setter
    def laboratory_fee(self, value):
        self.lab_fee = value

    @property
    def other_charges(self):
        return self.other_fee

    @other_charges.setter
    def other_charges(self, value):
        self.other_fee = value

    @property
    def development_fee(self):
        return 0.0

    @development_fee.setter
    def development_fee(self, value):
        self.other_fee = (self.other_fee or 0.0) + (value or 0.0)

    # Relationships
    student_fees = db.relationship('StudentFee', backref='fee_structure', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<FeeStructure {self.title} - ₹{self.total_amount}>'


class StudentFee(db.Model):
    __tablename__ = 'student_fees'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    fee_structure_id = db.Column(db.Integer, db.ForeignKey('fee_structures.id', ondelete='CASCADE'), nullable=False)
    
    total_amount = db.Column(db.Float, nullable=False)
    discount_amount = db.Column(db.Float, default=0.0, nullable=False)
    net_payable = db.Column(db.Float, nullable=False, default=0.0)
    paid_amount = db.Column(db.Float, default=0.0, nullable=False)
    pending_amount = db.Column(db.Float, nullable=False, default=0.0)
    
    status = db.Column(db.String(30), default='Pending', nullable=False)  # Pending, Partial, Paid, Overdue
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    payments = db.relationship('FeePayment', backref='student_fee', lazy='dynamic', cascade='all, delete-orphan')
    student = db.relationship('Student', backref=db.backref('fee_records', lazy='dynamic', overlaps="student_fees,student_record"), overlaps="student_fees,student_record")

    @property
    def due_amount(self):
        return self.pending_amount

    @due_amount.setter
    def due_amount(self, value):
        self.pending_amount = value

    def update_balance(self):
        self.paid_amount = sum([p.amount for p in self.payments if p.status in ('Success', 'Completed', 'Paid')])
        payable = self.net_payable if self.net_payable else self.total_amount
        self.pending_amount = max(0.0, payable - self.paid_amount)
        if self.paid_amount >= payable and payable > 0:
            self.status = 'Paid'
        elif self.paid_amount > 0:
            self.status = 'Partial'
        else:
            self.status = 'Pending'

    def __repr__(self):
        return f'<StudentFee Student:{self.student_id} Status:{self.status} Pending:{self.pending_amount}>'


# Alias for backward compatibility
StudentFeeRecord = StudentFee


class FeePayment(db.Model):
    __tablename__ = 'fee_payments'

    id = db.Column(db.Integer, primary_key=True)
    student_fee_id = db.Column(db.Integer, db.ForeignKey('student_fees.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    
    receipt_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    payment_mode = db.Column(db.String(50), default='Online', nullable=False)  # Online, Cash, Cheque, Demand Draft, UPI
    transaction_id = db.Column(db.String(100), unique=True, nullable=True)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(30), default='Success', nullable=False)  # Success, Failed, Refunded
    notes = db.Column(db.String(255), nullable=True)
    collected_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    # Relationships
    student = db.relationship('Student', backref=db.backref('all_payments', lazy='dynamic'))
    collected_by = db.relationship('User', foreign_keys=[collected_by_id])

    @property
    def amount_paid(self):
        return self.amount

    @amount_paid.setter
    def amount_paid(self, value):
        self.amount = value

    @property
    def student_fee_record_id(self):
        return self.student_fee_id

    @student_fee_record_id.setter
    def student_fee_record_id(self, value):
        self.student_fee_id = value

    def __repr__(self):
        return f'<FeePayment Receipt:{self.receipt_number} Amount:₹{self.amount}>'

