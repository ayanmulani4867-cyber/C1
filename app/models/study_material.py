from datetime import datetime
from app.extensions import db


class StudyMaterial(db.Model):
    __tablename__ = 'study_materials'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    class_division_id = db.Column(db.Integer, db.ForeignKey('class_divisions.id', ondelete='CASCADE'), nullable=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='CASCADE'), nullable=True)
    
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(20), default='PDF', nullable=False)  # PDF, PPT, PPTX, DOC, DOCX, etc.
    file_size_kb = db.Column(db.Float, default=0.0, nullable=True)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def created_at(self):
        return self.upload_date

    @property
    def file_size_bytes(self):
        return int((self.file_size_kb or 0.0) * 1024)

    @file_size_bytes.setter
    def file_size_bytes(self, val):
        self.file_size_kb = (val or 0) / 1024.0

    def __repr__(self):
        return f'<StudyMaterial {self.title} - Subject:{self.subject_id}>'
