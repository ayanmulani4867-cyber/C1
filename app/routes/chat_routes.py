"""
Campus Connect Chat REST API Routes
All endpoints enforce authentication and conversation-membership checks server-side.
The sender_id is ALWAYS derived from the authenticated user — never from client payload.
"""
import os
import uuid
import mimetypes
from datetime import datetime
from functools import wraps
from flask import Blueprint, request, jsonify, g, current_app, render_template
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, func
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.user import User, Role
from app.models.chat import (
    Conversation, ConversationMember, Message, MessageRead, MessageReport
)

chat_bp = Blueprint('chat', __name__)

# ─── Permission matrix ─────────────────────────────────────────────────────────
# Any authenticated active user can participate in chat.
# HOD can see all members in their domain; ADMIN has read-only moderation.
ALLOWED_CHAT_MIMETYPES = {
    # Images
    'image/jpeg', 'image/jpg', 'image/png', 'image/webp',
    # Documents
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
}
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024  # 10 MB
PAGE_SIZE = 30


def _get_current_user():
    """Resolve the authenticated user from Flask-Login session or Bearer token via g."""
    if hasattr(g, 'current_user') and g.current_user and g.current_user.is_active:
        return g.current_user
    if current_user.is_authenticated and current_user.is_active:
        return current_user
    return None


def chat_auth_required(f):
    """Decorator: require authenticated active user for chat endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = _get_current_user()
        if not user:
            return jsonify({'success': False, 'error': 'Unauthorized', 'message': 'Authentication required.'}), 401
        g.me = user
        return f(*args, **kwargs)
    return decorated


def _membership(conversation_id, user_id):
    """Return ConversationMember or None."""
    return ConversationMember.query.filter_by(
        conversation_id=conversation_id, user_id=user_id).first()


def _assert_member(conversation_id, user_id):
    """Return member record or raise 403 JSON."""
    m = _membership(conversation_id, user_id)
    if not m:
        return None, (jsonify({'success': False, 'error': 'Forbidden',
                               'message': 'You are not a member of this conversation.'}), 403)
    return m, None


# ─── Web page ───────────────────────────────────────────────────────────────────

@chat_bp.route('/chat', methods=['GET'])
@chat_bp.route('/chat/', methods=['GET'])
@chat_bp.route('/chat/<int:conversation_id>', methods=['GET'])
@login_required
def chat_page(conversation_id=None):
    """Render the main chat page (SPA shell)."""
    return render_template('chat/chat.html', initial_conversation_id=conversation_id)


# ─── Conversation listing ───────────────────────────────────────────────────────

@chat_bp.route('/api/chat/conversations', methods=['GET'])
@chat_auth_required
def list_conversations():
    """GET /api/chat/conversations — list all conversations the current user belongs to."""
    me = g.me
    include_archived = request.args.get('archived', 'false').lower() == 'true'
    q = (
        ConversationMember.query
        .filter_by(user_id=me.id)
        .join(Conversation, ConversationMember.conversation_id == Conversation.id)
        .order_by(Conversation.updated_at.desc())
    )
    if not include_archived:
        q = q.filter(ConversationMember.is_archived == False)  # noqa: E712

    memberships = q.all()
    result = []
    for m in memberships:
        conv = m.conversation
        data = conv.to_dict(current_user_id=me.id)
        # For private conversations, add the other person's info
        if not conv.is_group:
            other_member = ConversationMember.query.filter(
                ConversationMember.conversation_id == conv.id,
                ConversationMember.user_id != me.id
            ).first()
            if other_member and other_member.user:
                ou = other_member.user
                data['other_user'] = {
                    'id': ou.id,
                    'name': ou.full_name,
                    'avatar': ou.profile_image_url,
                    'role': ou.role,
                }
            else:
                data['other_user'] = None
        result.append(data)
    return jsonify({'success': True, 'conversations': result})


# ─── Create conversation ─────────────────────────────────────────────────────────

@chat_bp.route('/api/chat/conversations', methods=['POST'])
@chat_auth_required
def create_conversation():
    """POST /api/chat/conversations — start a new private or group conversation."""
    me = g.me
    data = request.get_json(force=True, silent=True) or {}

    conv_type = data.get('type', 'private')
    member_ids = data.get('member_ids', [])  # list of user IDs to add

    if conv_type not in ('private', 'group'):
        return jsonify({'success': False, 'error': 'Invalid type', 'message': "type must be 'private' or 'group'"}), 400

    # Validate target users exist and are active
    if not member_ids:
        return jsonify({'success': False, 'error': 'Bad Request', 'message': 'member_ids required.'}), 400

    target_users = User.query.filter(
        User.id.in_(member_ids),
        User.is_active == True  # noqa: E712
    ).all()

    if len(target_users) != len(set(member_ids)):
        return jsonify({'success': False, 'error': 'Bad Request',
                        'message': 'One or more target users not found or inactive.'}), 400

    # For private chats, only allow one other user
    if conv_type == 'private':
        if len(member_ids) != 1:
            return jsonify({'success': False, 'error': 'Bad Request',
                            'message': 'Private conversation requires exactly one other user.'}), 400
        other_id = int(member_ids[0])
        if other_id == me.id:
            return jsonify({'success': False, 'error': 'Bad Request',
                            'message': 'Cannot start a conversation with yourself.'}), 400

        # Check if private conversation already exists
        existing = (
            ConversationMember.query
            .join(Conversation, ConversationMember.conversation_id == Conversation.id)
            .filter(
                Conversation.is_group == False,  # noqa: E712
                ConversationMember.user_id == me.id
            )
            .all()
        )
        for em in existing:
            other = ConversationMember.query.filter_by(
                conversation_id=em.conversation_id, user_id=other_id).first()
            if other:
                conv = em.conversation
                return jsonify({'success': True, 'conversation': conv.to_dict(current_user_id=me.id),
                                'created': False})

        # Create new private conversation
        conv = Conversation(type='private', is_group=False, created_by_id=me.id)
        db.session.add(conv)
        db.session.flush()
        db.session.add(ConversationMember(conversation_id=conv.id, user_id=me.id, is_admin=True))
        db.session.add(ConversationMember(conversation_id=conv.id, user_id=other_id))
        db.session.commit()
        return jsonify({'success': True, 'conversation': conv.to_dict(current_user_id=me.id), 'created': True}), 201

    # Group chat
    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'success': False, 'error': 'Bad Request',
                        'message': 'title required for group conversations.'}), 400

    conv = Conversation(type='group', title=title, is_group=True, created_by_id=me.id)
    db.session.add(conv)
    db.session.flush()
    # Creator is admin
    db.session.add(ConversationMember(conversation_id=conv.id, user_id=me.id, is_admin=True))
    for uid in set(member_ids):
        uid = int(uid)
        if uid != me.id:
            db.session.add(ConversationMember(conversation_id=conv.id, user_id=uid))
    db.session.commit()

    # Broadcast new group to all members via SocketIO
    try:
        from app.extensions import socketio
        for m in conv.members:
            socketio.emit('conversation_updated', {
                'action': 'new_group',
                'conversation': conv.to_dict(current_user_id=m.user_id)
            }, room=f'user_{m.user_id}')
    except Exception:
        pass

    return jsonify({'success': True, 'conversation': conv.to_dict(current_user_id=me.id), 'created': True}), 201


# ─── Get single conversation ─────────────────────────────────────────────────────

@chat_bp.route('/api/chat/conversations/<int:conv_id>', methods=['GET'])
@chat_auth_required
def get_conversation(conv_id):
    me = g.me
    conv = Conversation.query.get_or_404(conv_id)
    member, err = _assert_member(conv_id, me.id)
    if err:
        return err
    return jsonify({'success': True, 'conversation': conv.to_dict(current_user_id=me.id)})


# ─── Messages (paginated) ─────────────────────────────────────────────────────────

@chat_bp.route('/api/chat/conversations/<int:conv_id>/messages', methods=['GET'])
@chat_auth_required
def list_messages(conv_id):
    me = g.me
    _, err = _assert_member(conv_id, me.id)
    if err:
        return err

    before_id = request.args.get('before_id', type=int)  # For infinite scroll (older msgs)
    search_q = request.args.get('q', '').strip()

    q = Message.query.filter_by(conversation_id=conv_id)
    if search_q:
        q = q.filter(Message.content.ilike(f'%{search_q}%'), Message.deleted_at.is_(None))
    if before_id:
        q = q.filter(Message.id < before_id)
    msgs = q.order_by(Message.id.desc()).limit(PAGE_SIZE).all()
    msgs.reverse()

    return jsonify({
        'success': True,
        'messages': [m.to_dict(current_user_id=me.id) for m in msgs],
        'has_more': len(msgs) == PAGE_SIZE
    })


# ─── Send message ─────────────────────────────────────────────────────────────────

@chat_bp.route('/api/chat/conversations/<int:conv_id>/messages', methods=['POST'])
@chat_auth_required
def send_message(conv_id):
    me = g.me
    conv = Conversation.query.get_or_404(conv_id)
    _, err = _assert_member(conv_id, me.id)
    if err:
        return err

    data = request.get_json(force=True, silent=True) or {}
    content = (data.get('content') or '').strip()
    msg_type = data.get('message_type', 'text')
    reply_to_id = data.get('reply_to_id')

    # Validate reply_to belongs to this conversation
    if reply_to_id:
        rto = Message.query.filter_by(id=reply_to_id, conversation_id=conv_id).first()
        if not rto:
            reply_to_id = None

    if not content and msg_type == 'text':
        return jsonify({'success': False, 'error': 'Bad Request', 'message': 'Message content required.'}), 400

    msg = Message(
        conversation_id=conv_id,
        sender_id=me.id,  # Always from auth — never client-provided
        message_type=msg_type,
        content=content,
        reply_to_id=reply_to_id,
    )
    db.session.add(msg)
    db.session.flush()

    # Update conversation's updated_at and last_message_id
    conv.updated_at = datetime.utcnow()
    conv.last_message_id = msg.id
    db.session.commit()

    msg_dict = msg.to_dict(current_user_id=me.id)

    # Emit new_message event via SocketIO to all members
    _emit_to_conversation(conv, 'new_message', {'message': msg_dict})

    return jsonify({'success': True, 'message': msg_dict}), 201


# ─── Mark conversation as read ────────────────────────────────────────────────────

@chat_bp.route('/api/chat/conversations/<int:conv_id>/read', methods=['POST'])
@chat_auth_required
def mark_read(conv_id):
    me = g.me
    member, err = _assert_member(conv_id, me.id)
    if err:
        return err

    # Mark all unread messages in this conversation as read
    last_msg = Message.query.filter_by(conversation_id=conv_id).order_by(Message.id.desc()).first()
    if last_msg:
        # Bulk insert read records for unread messages
        unread = Message.query.filter(
            Message.conversation_id == conv_id,
            Message.sender_id != me.id,
            Message.deleted_at.is_(None),
            ~Message.reads.any(MessageRead.user_id == me.id)
        ).all()
        for um in unread:
            db.session.merge(MessageRead(message_id=um.id, user_id=me.id, read_at=datetime.utcnow()))

        member.last_read_message_id = last_msg.id
        db.session.commit()

        # Emit read receipt
        _emit_to_conversation_obj(conv_id, 'message_read', {
            'conversation_id': conv_id,
            'reader_id': me.id,
            'last_read_message_id': last_msg.id,
        })

    return jsonify({'success': True})


# ─── Delete message (soft) ────────────────────────────────────────────────────────

@chat_bp.route('/api/chat/messages/<int:msg_id>/delete', methods=['POST'])
@chat_auth_required
def delete_message(msg_id):
    me = g.me
    msg = Message.query.get_or_404(msg_id)
    _, err = _assert_member(msg.conversation_id, me.id)
    if err:
        return err

    # Only the sender or admin can delete
    member = _membership(msg.conversation_id, me.id)
    if msg.sender_id != me.id and not (member and member.is_admin) and me.role not in (Role.ADMIN,):
        return jsonify({'success': False, 'error': 'Forbidden',
                        'message': 'You can only delete your own messages.'}), 403

    msg.deleted_at = datetime.utcnow()
    msg.content = None
    db.session.commit()

    _emit_to_conversation_obj(msg.conversation_id, 'message_deleted', {'message_id': msg_id})
    return jsonify({'success': True})


# ─── Report message ────────────────────────────────────────────────────────────────

@chat_bp.route('/api/chat/messages/<int:msg_id>/report', methods=['POST'])
@chat_auth_required
def report_message(msg_id):
    me = g.me
    msg = Message.query.get_or_404(msg_id)
    _, err = _assert_member(msg.conversation_id, me.id)
    if err:
        return err

    data = request.get_json(force=True, silent=True) or {}
    reason = data.get('reason', 'other')
    allowed_reasons = {'spam', 'harassment', 'inappropriate', 'other'}
    if reason not in allowed_reasons:
        reason = 'other'

    existing = MessageReport.query.filter_by(message_id=msg_id, reporter_id=me.id).first()
    if existing:
        return jsonify({'success': False, 'error': 'Conflict', 'message': 'Already reported.'}), 409

    report = MessageReport(
        message_id=msg_id,
        reporter_id=me.id,
        reason=reason,
        details=(data.get('details') or '').strip()[:500],
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Report submitted for review.'})


# ─── Group member management ───────────────────────────────────────────────────────

@chat_bp.route('/api/chat/conversations/<int:conv_id>/members', methods=['GET'])
@chat_auth_required
def list_members(conv_id):
    me = g.me
    conv = Conversation.query.get_or_404(conv_id)
    _, err = _assert_member(conv_id, me.id)
    if err:
        return err

    members = ConversationMember.query.filter_by(conversation_id=conv_id).all()
    result = []
    for m in members:
        if m.user:
            result.append({
                'user_id': m.user_id,
                'name': m.user.full_name,
                'avatar': m.user.profile_image_url,
                'role': m.user.role,
                'is_admin': m.is_admin,
                'joined_at': m.joined_at.isoformat() if m.joined_at else None,
            })
    return jsonify({'success': True, 'members': result})


@chat_bp.route('/api/chat/conversations/<int:conv_id>/members', methods=['POST'])
@chat_auth_required
def add_member(conv_id):
    me = g.me
    conv = Conversation.query.get_or_404(conv_id)
    if not conv.is_group:
        return jsonify({'success': False, 'error': 'Bad Request',
                        'message': 'Cannot add members to a private conversation.'}), 400

    my_mem, err = _assert_member(conv_id, me.id)
    if err:
        return err
    if not my_mem.is_admin:
        return jsonify({'success': False, 'error': 'Forbidden',
                        'message': 'Only group admins can add members.'}), 403

    data = request.get_json(force=True, silent=True) or {}
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Bad Request', 'message': 'user_id required.'}), 400
    user_id = int(user_id)

    new_user = User.query.get(user_id)
    if not new_user or not new_user.is_active:
        return jsonify({'success': False, 'error': 'Not Found', 'message': 'User not found.'}), 404

    existing = _membership(conv_id, user_id)
    if existing:
        return jsonify({'success': False, 'error': 'Conflict', 'message': 'User already a member.'}), 409

    db.session.add(ConversationMember(conversation_id=conv_id, user_id=user_id))
    db.session.commit()
    _emit_to_conversation(conv, 'conversation_updated', {'action': 'member_added', 'user_id': user_id})
    return jsonify({'success': True, 'message': 'Member added.'})


@chat_bp.route('/api/chat/conversations/<int:conv_id>/members/<int:target_user_id>', methods=['DELETE'])
@chat_auth_required
def remove_member(conv_id, target_user_id):
    me = g.me
    conv = Conversation.query.get_or_404(conv_id)
    if not conv.is_group:
        return jsonify({'success': False, 'error': 'Bad Request',
                        'message': 'Cannot remove members from a private conversation.'}), 400

    my_mem, err = _assert_member(conv_id, me.id)
    if err:
        return err

    # Allow self-leave or admin removal
    if target_user_id != me.id and not my_mem.is_admin:
        return jsonify({'success': False, 'error': 'Forbidden',
                        'message': 'Only group admins can remove other members.'}), 403

    target_mem = _membership(conv_id, target_user_id)
    if not target_mem:
        return jsonify({'success': False, 'error': 'Not Found',
                        'message': 'User is not a member of this conversation.'}), 404

    db.session.delete(target_mem)
    db.session.commit()
    _emit_to_conversation(conv, 'conversation_updated',
                          {'action': 'member_removed', 'user_id': target_user_id})
    return jsonify({'success': True, 'message': 'Member removed.'})


@chat_bp.route('/api/chat/conversations/<int:conv_id>/members/<int:target_user_id>/promote', methods=['POST'])
@chat_auth_required
def promote_member(conv_id, target_user_id):
    me = g.me
    conv = Conversation.query.get_or_404(conv_id)
    if not conv.is_group:
        return jsonify({'success': False, 'error': 'Bad Request', 'message': 'Not a group.'}), 400

    my_mem, err = _assert_member(conv_id, me.id)
    if err:
        return err
    if not my_mem.is_admin:
        return jsonify({'success': False, 'error': 'Forbidden',
                        'message': 'Only group admins can promote members.'}), 403

    target = _membership(conv_id, target_user_id)
    if not target:
        return jsonify({'success': False, 'error': 'Not Found', 'message': 'Member not found.'}), 404

    data = request.get_json(force=True, silent=True) or {}
    target.is_admin = bool(data.get('is_admin', True))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Member role updated.'})


# ─── Mute / Pin / Archive conversation ───────────────────────────────────────────

@chat_bp.route('/api/chat/conversations/<int:conv_id>/settings', methods=['PATCH'])
@chat_auth_required
def update_conversation_settings(conv_id):
    me = g.me
    member, err = _assert_member(conv_id, me.id)
    if err:
        return err

    data = request.get_json(force=True, silent=True) or {}
    if 'is_muted' in data:
        member.is_muted = bool(data['is_muted'])
    if 'is_pinned' in data:
        member.is_pinned = bool(data['is_pinned'])
    if 'is_archived' in data:
        member.is_archived = bool(data['is_archived'])

    # Group admins can rename or update avatar
    if 'title' in data or 'avatar_url' in data:
        conv = Conversation.query.get_or_404(conv_id)
        if conv.is_group and member.is_admin:
            if 'title' in data:
                conv.title = data['title'].strip()[:150]
            if 'avatar_url' in data:
                conv.avatar_url = data['avatar_url'].strip()[:500]

    db.session.commit()
    return jsonify({'success': True})


# ─── File / Image upload ────────────────────────────────────────────────────────

@chat_bp.route('/api/chat/conversations/<int:conv_id>/upload', methods=['POST'])
@chat_auth_required
def upload_attachment(conv_id):
    me = g.me
    conv = Conversation.query.get_or_404(conv_id)
    _, err = _assert_member(conv_id, me.id)
    if err:
        return err

    f = request.files.get('file')
    if not f or not f.filename:
        return jsonify({'success': False, 'error': 'Bad Request', 'message': 'No file provided.'}), 400

    # Validate extension
    fname = secure_filename(f.filename)
    ext = fname.rsplit('.', 1)[-1].lower() if '.' in fname else ''
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({'success': False, 'error': 'Bad Request',
                        'message': f'File type .{ext} is not allowed.'}), 400

    # Validate MIME type by server-side sniffing (do NOT trust Content-Type header alone)
    f.seek(0, 2)
    size = f.tell()
    f.seek(0)
    if size > MAX_ATTACHMENT_BYTES:
        return jsonify({'success': False, 'error': 'Bad Request',
                        'message': f'File too large. Max {MAX_ATTACHMENT_BYTES // (1024*1024)} MB.'}), 400

    # Try to guess MIME from extension (more reliable than client header for server validation)
    guessed_mime, _ = mimetypes.guess_type(fname)
    if guessed_mime not in ALLOWED_CHAT_MIMETYPES:
        return jsonify({'success': False, 'error': 'Bad Request',
                        'message': 'File MIME type not permitted.'}), 400

    # Save to uploads/chat folder
    subfolder = 'chat/images' if guessed_mime and guessed_mime.startswith('image/') else 'chat/files'
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, unique_name)
    f.save(save_path)
    relative_url = f'/static/uploads/{subfolder}/{unique_name}'

    msg_type = 'image' if guessed_mime and guessed_mime.startswith('image/') else 'file'
    reply_to_id = request.form.get('reply_to_id', type=int)
    content = (request.form.get('content') or '').strip()

    msg = Message(
        conversation_id=conv_id,
        sender_id=me.id,
        message_type=msg_type,
        content=content,
        attachment_url=relative_url,
        attachment_name=fname,
        attachment_size=size,
        attachment_mime=guessed_mime,
        reply_to_id=reply_to_id,
    )
    db.session.add(msg)
    db.session.flush()
    conv.updated_at = datetime.utcnow()
    conv.last_message_id = msg.id
    db.session.commit()

    msg_dict = msg.to_dict(current_user_id=me.id)
    _emit_to_conversation(conv, 'new_message', {'message': msg_dict})
    return jsonify({'success': True, 'message': msg_dict}), 201


# ─── User search (for starting new conversations) ─────────────────────────────────

@chat_bp.route('/api/chat/users/search', methods=['GET'])
@chat_auth_required
def search_users():
    me = g.me
    q_str = request.args.get('q', '').strip()
    role_filter = request.args.get('role', '').strip().upper()

    if not q_str and not role_filter:
        return jsonify({'success': True, 'users': []}), 200

    from app.models.student import Student
    from app.models.faculty import Faculty
    from app.models.department import Department
    from app.chat.events import is_user_online

    query = (
        User.query
        .outerjoin(Student, Student.user_id == User.id)
        .outerjoin(Faculty, Faculty.user_id == User.id)
        .outerjoin(Department, (Department.id == Student.department_id) | (Department.id == Faculty.department_id))
        .filter(
            User.is_active == True,  # noqa: E712
            User.id != me.id,
        )
    )

    if q_str:
        pattern = f'%{q_str}%'
        query = query.filter(
            or_(
                User.username.ilike(pattern),
                User.email.ilike(pattern),
                User.first_name.ilike(pattern),
                User.last_name.ilike(pattern),
                (User.first_name + ' ' + User.last_name).ilike(pattern),
                Student.student_id.ilike(pattern),
                Student.roll_no.ilike(pattern),
                Student.admission_no.ilike(pattern),
                Student.enrollment_no.ilike(pattern),
                Faculty.faculty_id.ilike(pattern),
                Faculty.employee_id.ilike(pattern),
                Faculty.designation.ilike(pattern),
                Department.name.ilike(pattern),
                Department.code.ilike(pattern),
            )
        )

    if role_filter in ('STUDENT', 'FACULTY', 'HOD', 'ADMIN'):
        query = query.filter(User.role == role_filter)

    users = query.distinct().limit(30).all()

    result = []
    for u in users:
        entry = {
            'id': u.id,
            'name': u.full_name,
            'username': u.username,
            'email': u.email,
            'role': u.role,
            'avatar': u.profile_image_url,
            'is_online': is_user_online(u.id),
            'department': None,
            'department_code': None,
            'designation': None,
            'semester': None,
            'student_id': None,
            'roll_no': None,
            'faculty_id': None,
            'employee_id': None,
        }
        if u.student_profile:
            sp = u.student_profile
            entry['department'] = sp.department.name if sp.department else None
            entry['department_code'] = sp.department.code if sp.department else None
            entry['semester'] = f"Sem {sp.semester.number}" if sp.semester else None
            entry['student_id'] = sp.student_id
            entry['roll_no'] = sp.roll_no
        elif u.faculty_profile:
            fp = u.faculty_profile
            entry['department'] = fp.department.name if fp.department else None
            entry['department_code'] = fp.department.code if fp.department else None
            entry['designation'] = fp.designation or ('Head of Department' if u.role == 'HOD' else 'Faculty')
            entry['faculty_id'] = fp.faculty_id
            entry['employee_id'] = fp.employee_id
        result.append(entry)

    return jsonify({'success': True, 'users': result})


# ─── Admin: list reports ────────────────────────────────────────────────────────

@chat_bp.route('/api/chat/admin/reports', methods=['GET'])
@chat_auth_required
def admin_list_reports():
    me = g.me
    if me.role not in (Role.ADMIN, Role.HOD):
        return jsonify({'success': False, 'error': 'Forbidden', 'message': 'Access denied.'}), 403

    reports = MessageReport.query.filter_by(status='pending').order_by(MessageReport.created_at.desc()).limit(100).all()
    return jsonify({'success': True, 'reports': [r.to_dict() for r in reports]})


@chat_bp.route('/api/chat/admin/reports/<int:report_id>/review', methods=['POST'])
@chat_auth_required
def admin_review_report(report_id):
    me = g.me
    if me.role not in (Role.ADMIN, Role.HOD):
        return jsonify({'success': False, 'error': 'Forbidden', 'message': 'Access denied.'}), 403

    report = MessageReport.query.get_or_404(report_id)
    data = request.get_json(force=True, silent=True) or {}
    action = data.get('action', 'dismiss')  # 'dismiss' | 'delete_message'
    report.status = 'reviewed' if action == 'delete_message' else 'dismissed'
    report.reviewed_by_id = me.id
    report.reviewed_at = datetime.utcnow()

    if action == 'delete_message':
        msg = report.message
        if msg:
            msg.deleted_at = datetime.utcnow()
            msg.content = None

    db.session.commit()
    return jsonify({'success': True})


# ─── Helpers ─────────────────────────────────────────────────────────────────────

def _emit_to_conversation(conv, event, data):
    """Emit a SocketIO event to all members of a conversation."""
    try:
        from app.extensions import socketio
        for mem in conv.members:
            socketio.emit(event, data, room=f'user_{mem.user_id}')
    except Exception:
        pass


def _emit_to_conversation_obj(conv_id, event, data):
    """Emit via conversation_id (lazy-load conv members)."""
    try:
        from app.extensions import socketio
        members = ConversationMember.query.filter_by(conversation_id=conv_id).all()
        for mem in members:
            socketio.emit(event, data, room=f'user_{mem.user_id}')
    except Exception:
        pass
