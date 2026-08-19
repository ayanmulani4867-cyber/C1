from datetime import datetime
from app.extensions import db


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    hod_faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='SET NULL', use_alter=True, name='fk_departments_hod_faculty_id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    courses = db.relationship('Course', backref='department', lazy='dynamic', cascade='all, delete-orphan')
    faculty_members = db.relationship('Faculty', foreign_keys='Faculty.department_id', backref='department', lazy='dynamic')
    students = db.relationship('Student', backref='department', lazy='dynamic')
    subjects = db.relationship('Subject', backref='department', lazy='dynamic')
    notices = db.relationship('Notice', backref='department', lazy='dynamic')

    # Specific relationship for the HOD
    hod = db.relationship('Faculty', foreign_keys=[hod_faculty_id], post_update=True)

    def __repr__(self):
        return f'<Department {self.code} - {self.name}>'
