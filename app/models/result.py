from datetime import datetime
from app.extensions import db


class ExamResult(db.Model):
    __tablename__ = 'exam_results'

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=True)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id', ondelete='CASCADE'), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey('academic_sessions.id', ondelete='CASCADE'), nullable=True)

    marks_obtained = db.Column(db.Float, nullable=False, default=0.0)
    max_marks = db.Column(db.Float, default=100.0, nullable=False)
    percentage = db.Column(db.Float, nullable=True, default=0.0)
    grade = db.Column(db.String(10), nullable=True, default='P')  # A+, A, B, C, D, F
    grade_point = db.Column(db.Float, default=0.0, nullable=False)
    is_passed = db.Column(db.Boolean, default=True, nullable=False)
    is_published = db.Column(db.Boolean, default=False, nullable=False)
    
    # Workflow status: Draft -> Submitted_By_Faculty -> Verified_By_HOD -> Published_By_Admin
    status = db.Column(db.String(30), default='Draft', nullable=False)
    entered_by_faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='SET NULL'), nullable=True)
    reviewed_by_hod_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='SET NULL'), nullable=True)
    published_by_admin_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    published_at = db.Column(db.DateTime, nullable=True)
    remarks = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    semester = db.relationship('Semester', foreign_keys=[semester_id])
    session = db.relationship('AcademicSession', foreign_keys=[session_id])

    __table_args__ = (
        db.UniqueConstraint('exam_id', 'student_id', name='uq_student_exam_result'),
    )


    @staticmethod
    def calculate_grade(marks, max_marks):
        pct = (marks / max_marks) * 100 if max_marks > 0 else 0
        if pct >= 90:
            return 'A+', 10.0, True
        elif pct >= 80:
            return 'A', 9.0, True
        elif pct >= 70:
            return 'B+', 8.0, True
        elif pct >= 60:
            return 'B', 7.0, True
        elif pct >= 50:
            return 'C', 6.0, True
        elif pct >= 40:
            return 'D', 5.0, True
        else:
            return 'F', 0.0, False

    def __repr__(self):
        return f'<ExamResult Student:{self.student_id} Subject:{self.subject_id} Marks:{self.marks_obtained}/{self.max_marks}>'
