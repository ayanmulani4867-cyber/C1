from datetime import datetime
from app.extensions import db


class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    feedback_type = db.Column(db.String(30), default='Faculty', nullable=False)  # Faculty, Course, Institutional, Facilities
    
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='SET NULL'), nullable=True)
    is_anonymous = db.Column(db.Boolean, default=False, nullable=False)
    
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='CASCADE'), nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=True)
    
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5 stars
    clarity_rating = db.Column(db.Integer, default=5, nullable=True)
    punctuality_rating = db.Column(db.Integer, default=5, nullable=True)
    helpfulness_rating = db.Column(db.Integer, default=5, nullable=True)
    
    comments = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    course = db.relationship('Course', foreign_keys=[course_id])
    department = db.relationship('Department', foreign_keys=[department_id])

    def __repr__(self):
        return f'<Feedback Type:{self.feedback_type} Rating:{self.rating}>'
