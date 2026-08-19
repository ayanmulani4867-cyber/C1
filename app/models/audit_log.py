from datetime import datetime
from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    username = db.Column(db.String(64), nullable=True)
    role = db.Column(db.String(20), nullable=True)
    
    action = db.Column(db.String(50), nullable=False)  # Login, Logout, Create, Update, Delete, PasswordChange, AttendanceMarked, ResultPublished, StatusChange
    module = db.Column(db.String(50), nullable=False)  # Auth, Student, Faculty, Department, Course, Subject, Timetable, Attendance, Result, Fee, Leave, Certificate, Complaint, Notice, Event
    record_id = db.Column(db.String(50), nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    @classmethod
    def log(cls, action, module, user=None, record_id=None, details=None, ip_address=None):
        try:
            log_entry = cls(
                user_id=user.id if user and hasattr(user, 'id') else None,
                username=user.username if user and hasattr(user, 'username') else 'Anonymous',
                role=user.role if user and hasattr(user, 'role') else 'None',
                action=action,
                module=module,
                record_id=str(record_id) if record_id else None,
                details=details,
                ip_address=ip_address
            )
            db.session.add(log_entry)
            db.session.commit()
        except Exception as e:
            db.session.rollback()

    def __repr__(self):
        return f'<AuditLog {self.username} - {self.action} on {self.module} at {self.created_at}>'
