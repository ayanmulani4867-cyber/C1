from app.extensions import db


class Semester(db.Model):
    __tablename__ = 'semesters'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, unique=True, nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)  # e.g., "Semester 1"
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    subjects = db.relationship('Subject', backref='semester', lazy='dynamic')
    students = db.relationship('Student', backref='semester', lazy='dynamic')
    class_divisions = db.relationship('ClassDivision', backref='semester', lazy='dynamic')
    timetables = db.relationship('Timetable', backref='semester', lazy='dynamic')
    exams = db.relationship('Exam', backref='semester', lazy='dynamic')
    fee_structures = db.relationship('FeeStructure', backref='semester', lazy='dynamic')

    def __repr__(self):
        return f'<Semester {self.name}>'
