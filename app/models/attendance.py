from datetime import datetime
from app.extensions import db


class AttendanceSession(db.Model):
    __tablename__ = 'attendance_sessions'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    time_slot = db.Column(db.String(50), nullable=True)  # e.g., "09:00 - 10:00"
    topic_covered = db.Column(db.String(255), nullable=True)
    
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='CASCADE'), nullable=False)
    class_division_id = db.Column(db.Integer, db.ForeignKey('class_divisions.id', ondelete='CASCADE'), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    records = db.relationship('AttendanceRecord', backref='session', lazy='dynamic', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('date', 'time_slot', 'subject_id', 'class_division_id', name='uq_attendance_session'),
    )

    def __repr__(self):
        return f'<AttendanceSession {self.date} Subject:{self.subject_id} Div:{self.class_division_id}>'


class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True)
    attendance_session_id = db.Column(db.Integer, db.ForeignKey('attendance_sessions.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), default='Present', nullable=False)  # Present, Absent, Late, Excused
    remarks = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('attendance_session_id', 'student_id', name='uq_student_attendance'),
    )

    def __repr__(self):
        return f'<AttendanceRecord Student:{self.student_id} Status:{self.status}>'
