from datetime import datetime
from app.extensions import db

# Association table for Faculty - Subject assignments (many-to-many)
faculty_subjects = db.Table(
    'faculty_subjects',
    db.Column('faculty_id', db.Integer, db.ForeignKey('faculty.id', ondelete='CASCADE'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), primary_key=True)
)


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    credits = db.Column(db.Integer, default=3, nullable=False)
    subject_type = db.Column(db.String(20), default='Theory', nullable=False)  # Theory, Practical, Elective
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    assigned_faculty = db.relationship('Faculty', secondary=faculty_subjects, backref=db.backref('assigned_subjects', lazy='dynamic'))
    timetables = db.relationship('Timetable', backref='subject', lazy='dynamic', cascade='all, delete-orphan')
    attendance_sessions = db.relationship('AttendanceSession', backref='subject', lazy='dynamic')
    exams = db.relationship('Exam', backref='subject', lazy='dynamic')
    assignments = db.relationship('Assignment', backref='subject', lazy='dynamic')
    study_materials = db.relationship('StudyMaterial', backref='subject', lazy='dynamic')
    exam_results = db.relationship('ExamResult', backref='subject', lazy='dynamic')

    def __repr__(self):
        return f'<Subject {self.code} - {self.name}>'
