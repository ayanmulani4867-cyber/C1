from datetime import datetime
from app.extensions import db


class Complaint(db.Model):
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    
    category = db.Column(db.String(50), nullable=False)  # Academic, Hostel, Infrastructure, Ragging, Fee, General
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=True)
    attachment_path = db.Column(db.String(255), nullable=True)
    
    status = db.Column(db.String(30), default='Submitted', nullable=False)  # Submitted, Assigned, In Progress, Resolved, Closed
    priority = db.Column(db.String(20), default='Medium', nullable=False)  # Low, Medium, High, Urgent
    
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id])

    def __repr__(self):
        return f'<Complaint {self.ticket_number} Status:{self.status}>'
