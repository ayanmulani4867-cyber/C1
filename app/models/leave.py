from datetime import datetime
from app.extensions import db


class LeaveRequest(db.Model):
    __tablename__ = 'leave_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='CASCADE'), nullable=True)
    applicant_role = db.Column(db.String(20), nullable=True)  # STUDENT, FACULTY
    
    leave_type = db.Column(db.String(50), nullable=False)  # Medical, Casual, Academic, Duty Leave, Emergency
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_days = db.Column(db.Integer, default=1, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    document_path = db.Column(db.String(255), nullable=True)
    
    status = db.Column(db.String(30), default='Pending', nullable=False)  # Pending, Approved, Rejected
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    review_comment = db.Column(db.Text, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], overlaps="applicant,leave_requests")
    student = db.relationship('Student', foreign_keys=[student_id], backref=db.backref('leave_applications', lazy='dynamic'))
    faculty = db.relationship('Faculty', foreign_keys=[faculty_id], backref=db.backref('leave_applications', lazy='dynamic'))
    reviewed_by = db.relationship('User', foreign_keys=[reviewed_by_id])

    @property
    def document_file(self):
        return self.document_path

    @document_file.setter
    def document_file(self, val):
        self.document_path = val

    @property
    def applied_at(self):
        return self.created_at

    @applied_at.setter
    def applied_at(self, val):
        self.created_at = val

    def __repr__(self):
        return f'<LeaveRequest User:{self.user_id} Status:{self.status} {self.start_date} to {self.end_date}>'


LeaveApplication = LeaveRequest

