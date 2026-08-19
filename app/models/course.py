from datetime import datetime
from app.extensions import db


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    duration_years = db.Column(db.Integer, default=4, nullable=False)
    total_semesters = db.Column(db.Integer, default=8, nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    subjects = db.relationship('Subject', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    students = db.relationship('Student', backref='course', lazy='dynamic')
    class_divisions = db.relationship('ClassDivision', backref='course', lazy='dynamic')
    fee_structures = db.relationship('FeeStructure', backref='course', lazy='dynamic')

    def __repr__(self):
        return f'<Course {self.code} - {self.name}>'
