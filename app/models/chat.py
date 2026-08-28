"""
Campus Connect Chat Models
Defines all database tables required for the real-time chat & messaging system.
Uses the EXISTING User model — no duplicate user/auth system created.
"""
from datetime import datetime
from app.extensions import db


class Conversation(db.Model):
    """A conversation between two or more users (private or group)."""
    __tablename__ = 'chat_conversations'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False, default='private')  # 'private' | 'group'
    title = db.Column(db.String(150), nullable=True)       # Used for group names
    avatar_url = db.Column(db.String(255), nullable=True)  # Group avatar
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, index=True)
    last_message_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id', ondelete='SET NULL',
                                                           use_alter=True, name='fk_conv_last_msg'), nullable=True)
    is_group = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by_id], backref='created_conversations')
    members = db.relationship('ConversationMember', backref='conversation', lazy='dynamic',
                              cascade='all, delete-orphan', foreign_keys='ConversationMember.conversation_id')
    messages = db.relationship('Message', backref='conversation', lazy='dynamic',
                               cascade='all, delete-orphan',
                               foreign_keys='Message.conversation_id',
                               primaryjoin='Conversation.id == Message.conversation_id')
    last_message = db.relationship('Message', foreign_keys=[last_message_id],
                                   primaryjoin='Conversation.last_message_id == Message.id',
                                   uselist=False, post_update=True)

    def to_dict(self, current_user_id=None):
        d = {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'avatar_url': self.avatar_url,
            'is_group': self.is_group,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if self.last_message:
            d['last_message'] = self.last_message.to_dict()
        else:
            d['last_message'] = None
        # Unread count for current user
        if current_user_id:
            member = ConversationMember.query.filter_by(
                conversation_id=self.id, user_id=current_user_id).first()
            if member:
                d['unread_count'] = member.unread_count
                d['is_muted'] = member.is_muted
                d['is_pinned'] = member.is_pinned
                d['is_archived'] = member.is_archived
            else:
                d['unread_count'] = 0
                d['is_muted'] = False
                d['is_pinned'] = False
                d['is_archived'] = False
        return d

    def __repr__(self):
        return f'<Conversation {self.id} [{self.type}]>'


class ConversationMember(db.Model):
    """Membership record linking a User to a Conversation with per-member settings."""
    __tablename__ = 'chat_conversation_members'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('chat_conversations.id', ondelete='CASCADE'),
                                nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False, index=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_read_message_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id', ondelete='SET NULL'), nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_muted = db.Column(db.Boolean, default=False, nullable=False)
    is_pinned = db.Column(db.Boolean, default=False, nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('conversation_id', 'user_id', name='uq_conv_member'),
        db.Index('ix_conv_member_user', 'conversation_id', 'user_id'),
    )

    # Relationships
    user = db.relationship('User', backref='conversation_memberships', foreign_keys=[user_id])
    last_read_message = db.relationship('Message', foreign_keys=[last_read_message_id])

    @property
    def unread_count(self):
        """Count of messages newer than last_read_message in this conversation."""
        from sqlalchemy import and_
        q = Message.query.filter(
            and_(
                Message.conversation_id == self.conversation_id,
                Message.sender_id != self.user_id,
                Message.deleted_at.is_(None),
            )
        )
        if self.last_read_message_id:
            q = q.filter(Message.id > self.last_read_message_id)
        else:
            q = q.filter(Message.id > 0)
        return q.count()

    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'is_admin': self.is_admin,
            'is_muted': self.is_muted,
            'is_pinned': self.is_pinned,
            'is_archived': self.is_archived,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
        }

    def __repr__(self):
        return f'<Member user={self.user_id} conv={self.conversation_id}>'


class Message(db.Model):
    """A single message inside a conversation."""
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('chat_conversations.id', ondelete='CASCADE'),
                                nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'),
                          nullable=True, index=True)
    message_type = db.Column(db.String(20), nullable=False, default='text')  # text|image|file|system
    content = db.Column(db.Text, nullable=True)
    attachment_url = db.Column(db.String(500), nullable=True)
    attachment_name = db.Column(db.String(255), nullable=True)
    attachment_size = db.Column(db.Integer, nullable=True)  # bytes
    attachment_mime = db.Column(db.String(100), nullable=True)
    reply_to_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    edited_at = db.Column(db.DateTime, nullable=True)
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft-delete

    # Relationships
    sender = db.relationship('User', backref='sent_messages', foreign_keys=[sender_id])
    reply_to = db.relationship('Message', remote_side=[id], foreign_keys=[reply_to_id],
                               backref='replies')
    reads = db.relationship('MessageRead', backref='message', lazy='dynamic',
                            cascade='all, delete-orphan')
    reports = db.relationship('MessageReport', backref='message', lazy='dynamic',
                              cascade='all, delete-orphan')

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def to_dict(self, current_user_id=None):
        sender_data = None
        if self.sender:
            sender_data = {
                'id': self.sender.id,
                'name': self.sender.full_name,
                'avatar': self.sender.profile_image_url,
                'role': self.sender.role,
            }
        reply_data = None
        if self.reply_to and not self.reply_to.is_deleted:
            reply_data = {
                'id': self.reply_to.id,
                'content': self.reply_to.content,
                'sender_name': self.reply_to.sender.full_name if self.reply_to.sender else 'Unknown',
                'message_type': self.reply_to.message_type,
            }
        read_by = [r.user_id for r in self.reads]
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_id': self.sender_id,
            'sender': sender_data,
            'message_type': self.message_type,
            'content': '[Deleted]' if self.is_deleted else self.content,
            'attachment_url': None if self.is_deleted else self.attachment_url,
            'attachment_name': None if self.is_deleted else self.attachment_name,
            'attachment_size': self.attachment_size,
            'attachment_mime': self.attachment_mime,
            'reply_to': reply_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'is_deleted': self.is_deleted,
            'read_by': read_by,
            'is_read_by_me': (current_user_id in read_by) if current_user_id else False,
            'is_mine': (self.sender_id == current_user_id) if current_user_id else False,
        }

    def __repr__(self):
        return f'<Message {self.id} conv={self.conversation_id}>'


class MessageRead(db.Model):
    """Tracks which users have read which messages (for delivery/read receipts)."""
    __tablename__ = 'chat_message_reads'

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id', ondelete='CASCADE'),
                           nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False, index=True)
    read_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('message_id', 'user_id', name='uq_msg_read'),
    )

    def __repr__(self):
        return f'<MessageRead msg={self.message_id} user={self.user_id}>'


class MessageReport(db.Model):
    """Stores user reports against messages for admin moderation."""
    __tablename__ = 'chat_message_reports'

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('chat_messages.id', ondelete='CASCADE'),
                           nullable=False, index=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'),
                            nullable=False, index=True)
    reason = db.Column(db.String(50), nullable=False)   # spam|harassment|inappropriate|other
    details = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending|reviewed|dismissed
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='message_reports')
    reviewed_by = db.relationship('User', foreign_keys=[reviewed_by_id])

    def to_dict(self):
        return {
            'id': self.id,
            'message_id': self.message_id,
            'reporter_id': self.reporter_id,
            'reason': self.reason,
            'details': self.details,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<MessageReport msg={self.message_id} reason={self.reason}>'
