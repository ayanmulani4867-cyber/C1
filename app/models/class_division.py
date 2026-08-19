from datetime import datetime
from app.extensions import db


class ClassDivision(db.Model):
    __tablename__ = 'class_divisions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # e.g., "A", "B", "CSE-4A"
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id', ondelete='CASCADE'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('academic_sessions.id', ondelete='CASCADE'), nullable=False)
    room_number = db.Column(db.String(30), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    department = db.relationship('Department', backref=db.backref('class_divisions', lazy='dynamic'))
    students = db.relationship('Student', backref='division', lazy='dynamic')
    timetables = db.relationship('Timetable', backref='class_division', lazy='dynamic', cascade='all, delete-orphan')
    attendance_sessions = db.relationship('AttendanceSession', backref='class_division', lazy='dynamic')
    assignments = db.relationship('Assignment', backref='class_division', lazy='dynamic')
    study_materials = db.relationship('StudyMaterial', backref='class_division', lazy='dynamic')
    exams = db.relationship('Exam', backref='class_division', lazy='dynamic')

    __table_args__ = (
        db.UniqueConstraint('name', 'course_id', 'semester_id', 'session_id', name='uq_class_division'),
    )

    @property
    def display_name(self):
        dept_code = self.department.code if self.department else ""
        sem_name = self.semester.name if self.semester else ""
        return f"{dept_code} - {sem_name} (Div {self.name})"

    def __repr__(self):
        return f'<ClassDivision {self.display_name}>'
