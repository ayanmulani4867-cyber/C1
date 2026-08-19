from datetime import datetime
from sqlalchemy.orm import synonym
from app.extensions import db


class Notice(db.Model):
    __tablename__ = 'notices'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    attachment_path = db.Column(db.String(255), nullable=True)
    
    target_audience = db.Column(db.String(30), default='ALL', nullable=False)  # ALL, DEPARTMENT, FACULTY, STUDENT
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=True)
    class_division_id = db.Column(db.Integer, db.ForeignKey('class_divisions.id', ondelete='CASCADE'), nullable=True)
    
    priority = db.Column(db.String(20), default='Normal', nullable=False)  # Low, Normal, High, Urgent
    publish_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    expiry_date = db.Column(db.Date, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_published = synonym('is_active')
    
    published_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_by_id = synonym('published_by_id')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    published_by = db.relationship('User', foreign_keys=[published_by_id])
    class_division = db.relationship('ClassDivision', foreign_keys=[class_division_id])

    @property
    def attachment_file(self):
        return self.attachment_path

    @attachment_file.setter
    def attachment_file(self, val):
        self.attachment_path = val

    def __repr__(self):
        return f'<Notice {self.title} Priority:{self.priority}>'
