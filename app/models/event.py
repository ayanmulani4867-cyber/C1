from datetime import datetime
from app.extensions import db


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_type = db.Column(db.String(50), default='Academic', nullable=False)  # Academic, Cultural, Sports, Workshop, Seminar, Hackathon
    venue = db.Column(db.String(100), nullable=False)
    
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    registration_deadline = db.Column(db.DateTime, nullable=True)
    
    max_participants = db.Column(db.Integer, default=0, nullable=True)  # 0 for unlimited
    is_open_for_registration = db.Column(db.Boolean, default=True, nullable=False)
    banner_image = db.Column(db.String(255), nullable=True)
    
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    created_by = db.relationship('User', foreign_keys=[created_by_id])
    registrations = db.relationship('EventRegistration', backref='event', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def registered_count(self):
        return self.registrations.filter_by(status='Confirmed').count()

    def __repr__(self):
        return f'<Event {self.title} Date:{self.start_datetime}>'


class EventRegistration(db.Model):
    __tablename__ = 'event_registrations'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    
    registration_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(30), default='Confirmed', nullable=False)  # Confirmed, Cancelled, Attended
    
    __table_args__ = (
        db.UniqueConstraint('event_id', 'student_id', name='uq_student_event_reg'),
    )

    def __repr__(self):
        return f'<EventRegistration Event:{self.event_id} Student:{self.student_id}>'


CampusEvent = Event
CampusEventRegistration = EventRegistration
