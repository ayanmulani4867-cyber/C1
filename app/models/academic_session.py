from datetime import datetime
from app.extensions import db


class AcademicSession(db.Model):
    __tablename__ = 'academic_sessions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)  # e.g., "2025-26", "2026-27"
    start_year = db.Column(db.Integer, nullable=False)
    end_year = db.Column(db.Integer, nullable=False)
    is_current = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    students = db.relationship('Student', backref='session', lazy='dynamic')
    class_divisions = db.relationship('ClassDivision', backref='session', lazy='dynamic')
    timetables = db.relationship('Timetable', backref='session', lazy='dynamic')
    exams = db.relationship('Exam', backref='session', lazy='dynamic')
    fee_structures = db.relationship('FeeStructure', backref='session', lazy='dynamic')

    def __repr__(self):
        return f'<AcademicSession {self.name}{" (Current)" if self.is_current else ""}>'
