from datetime import datetime
from app.extensions import db
from app.models.result import ExamResult


class Exam(db.Model):
    __tablename__ = 'exams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Mid-Term Examination March 2026"
    exam_type = db.Column(db.String(30), default='Midterm', nullable=False)  # Internal, Midterm, Practical, End Semester
    
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    class_division_id = db.Column(db.Integer, db.ForeignKey('class_divisions.id', ondelete='CASCADE'), nullable=True)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id', ondelete='CASCADE'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('academic_sessions.id', ondelete='CASCADE'), nullable=False)
    
    exam_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    room_number = db.Column(db.String(50), nullable=True)
    max_marks = db.Column(db.Float, default=100.0, nullable=False)
    passing_marks = db.Column(db.Float, default=40.0, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    results = db.relationship('ExamResult', backref='exam', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def title(self):
        return self.name

    @title.setter
    def title(self, val):
        self.name = val

    def __repr__(self):
        return f'<Exam {self.name} - Subject:{self.subject_id}>'
