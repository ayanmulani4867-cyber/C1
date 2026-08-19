import uuid
from datetime import datetime
from app.extensions import db


class CertificateRequest(db.Model):
    __tablename__ = 'certificate_requests'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    
    certificate_type = db.Column(db.String(50), nullable=False)  # Bonafide, Character Certificate, Fee Certificate, Course Completion, Medium of Instruction
    purpose = db.Column(db.Text, nullable=False)
    
    status = db.Column(db.String(30), default='Pending', nullable=False)  # Pending, Approved, Rejected, Issued
    certificate_number = db.Column(db.String(50), unique=True, nullable=True, index=True)
    verification_code = db.Column(db.String(64), unique=True, default=lambda: str(uuid.uuid4().hex[:12].upper()), nullable=False, index=True)
    
    approved_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    issued_date = db.Column(db.Date, nullable=True)
    pdf_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    approved_by = db.relationship('User', foreign_keys=[approved_by_id])

    @property
    def requested_at(self):
        return self.created_at

    @requested_at.setter
    def requested_at(self, val):
        self.created_at = val

    def __repr__(self):
        return f'<CertificateRequest Student:{self.student_id} Type:{self.certificate_type} Status:{self.status}>'
