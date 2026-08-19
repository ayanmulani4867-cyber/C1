from datetime import datetime
from app.extensions import db
from app.models.study_material import StudyMaterial


class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    class_division_id = db.Column(db.Integer, db.ForeignKey('class_divisions.id', ondelete='CASCADE'), nullable=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='CASCADE'), nullable=True)
    
    due_date = db.Column(db.DateTime, nullable=False)
    max_marks = db.Column(db.Float, default=20.0, nullable=False)
    attachment_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    submissions = db.relationship('AssignmentSubmission', backref='assignment', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def attachment_file(self):
        return self.attachment_path

    @attachment_file.setter
    def attachment_file(self, val):
        self.attachment_path = val

    @property
    def file_path(self):
        return self.attachment_path

    @file_path.setter
    def file_path(self, val):
        self.attachment_path = val

    def __repr__(self):
        return f'<Assignment {self.title} - Due:{self.due_date}>'


class AssignmentSubmission(db.Model):
    __tablename__ = 'assignment_submissions'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    
    submission_file = db.Column(db.String(255), nullable=True)
    submission_text = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    marks_obtained = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    evaluated_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(30), default='Submitted', nullable=False)  # Submitted, Graded, Resubmission Requested

    __table_args__ = (
        db.UniqueConstraint('assignment_id', 'student_id', name='uq_student_assignment_submission'),
    )

    @property
    def file_path(self):
        return self.submission_file

    @file_path.setter
    def file_path(self, val):
        self.submission_file = val

    def __repr__(self):
        return f'<AssignmentSubmission Assignment:{self.assignment_id} Student:{self.student_id} Status:{self.status}>'
