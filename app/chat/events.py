"""
Campus Connect Chat WebSocket Events (Flask-SocketIO)
Handles real-time presence, typing indicators, join/leave rooms,
message delivery & read receipts.

Authentication: Every connect event verifies the session or Bearer token.
Sender identity is always from the authenticated user — never from client payload.
"""
from datetime import datetime
from flask import request, g
from flask_socketio import emit, join_room, leave_room, disconnect
from app.extensions import socketio, db
from app.models.chat import ConversationMember, MessageRead, Message


# ─── In-memory presence store ────────────────────────────────────────────────────
# Maps user_id → set of socket session IDs (handles multiple tabs)
_online_users: dict[int, set] = {}


def _get_auth_user():
    """Resolve authenticated user for SocketIO connections."""
    from flask_login import current_user
    if current_user.is_authenticated and current_user.is_active:
        return current_user
    # Bearer token via query string (used by Android / API clients)
    token = request.args.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    if token:
        try:
            from app.utils.api_auth import verify_api_token
            user, _, _ = verify_api_token(token)
            if user and user.is_active:
                return user
        except Exception:
            pass
    return None


# ─── Connection ────────────────────────────────────────────────────────────────

@socketio.on('connect')
def handle_connect():
    user = _get_auth_user()
    if not user:
        disconnect()
        return False  # Reject connection

    # Join a personal room so server can target this user specifically
    join_room(f'user_{user.id}')

    # Track presence
    if user.id not in _online_users:
        _online_users[user.id] = set()
    _online_users[user.id].add(request.sid)

    # Broadcast online status to all connected users who share a conversation
    _broadcast_presence(user.id, online=True)

    emit('connected', {'user_id': user.id, 'status': 'online'})


@socketio.on('disconnect')
def handle_disconnect():
    user = _get_auth_user()
    if not user:
        return

    leave_room(f'user_{user.id}')

    if user.id in _online_users:
        _online_users[user.id].discard(request.sid)
        if not _online_users[user.id]:
            del _online_users[user.id]
            _broadcast_presence(user.id, online=False)


# ─── Join / Leave conversation rooms ─────────────────────────────────────────────

@socketio.on('join_conversation')
def handle_join_conversation(data):
    """Client joins a socket room for a specific conversation."""
    user = _get_auth_user()
    if not user:
        return

    conv_id = data.get('conversation_id')
    if not conv_id:
        return

    # Verify membership server-side
    member = ConversationMember.query.filter_by(
        conversation_id=conv_id, user_id=user.id).first()
    if not member:
        emit('error', {'message': 'Not a member of this conversation.'})
        return

    join_room(f'conv_{conv_id}')
    emit('joined_conversation', {'conversation_id': conv_id})


@socketio.on('leave_conversation')
def handle_leave_conversation(data):
    user = _get_auth_user()
    if not user:
        return
    conv_id = data.get('conversation_id')
    if conv_id:
        leave_room(f'conv_{conv_id}')


# ─── Typing indicators ─────────────────────────────────────────────────────────

@socketio.on('typing_start')
def handle_typing_start(data):
    """Relay typing start event to other conversation members. No DB write."""
    user = _get_auth_user()
    if not user:
        return

    conv_id = data.get('conversation_id')
    if not conv_id:
        return

    member = ConversationMember.query.filter_by(
        conversation_id=conv_id, user_id=user.id).first()
    if not member:
        return

    # Emit to all OTHER members of this conversation
    members = ConversationMember.query.filter(
        ConversationMember.conversation_id == conv_id,
        ConversationMember.user_id != user.id
    ).all()
    for m in members:
        socketio.emit('typing_start', {
            'conversation_id': conv_id,
            'user_id': user.id,
            'user_name': user.full_name,
        }, room=f'user_{m.user_id}')


@socketio.on('typing_stop')
def handle_typing_stop(data):
    """Relay typing stop event."""
    user = _get_auth_user()
    if not user:
        return

    conv_id = data.get('conversation_id')
    if not conv_id:
        return

    member = ConversationMember.query.filter_by(
        conversation_id=conv_id, user_id=user.id).first()
    if not member:
        return

    members = ConversationMember.query.filter(
        ConversationMember.conversation_id == conv_id,
        ConversationMember.user_id != user.id
    ).all()
    for m in members:
        socketio.emit('typing_stop', {
            'conversation_id': conv_id,
            'user_id': user.id,
        }, room=f'user_{m.user_id}')


# ─── Message delivered ─────────────────────────────────────────────────────────

@socketio.on('message_delivered')
def handle_message_delivered(data):
    """Mark message as delivered (client acknowledges receipt)."""
    user = _get_auth_user()
    if not user:
        return

    msg_id = data.get('message_id')
    if not msg_id:
        return

    msg = Message.query.get(msg_id)
    if not msg:
        return

    # Ensure the receiver is a member of the conversation
    member = ConversationMember.query.filter_by(
        conversation_id=msg.conversation_id, user_id=user.id).first()
    if not member:
        return

    # Notify the sender
    if msg.sender_id and msg.sender_id != user.id:
        socketio.emit('message_delivered', {
            'message_id': msg_id,
            'delivered_to': user.id,
        }, room=f'user_{msg.sender_id}')


# ─── Online status query ────────────────────────────────────────────────────────

@socketio.on('get_online_users')
def handle_get_online_users(data):
    """Return which of the requested user_ids are currently online."""
    user_ids = data.get('user_ids', [])
    online = [uid for uid in user_ids if uid in _online_users]
    emit('online_users', {'online_user_ids': online})


def is_user_online(user_id: int) -> bool:
    return user_id in _online_users


# ─── Internal helpers ──────────────────────────────────────────────────────────

def _broadcast_presence(user_id: int, online: bool):
    """Broadcast online/offline status to all contacts of user_id."""
    event = 'user_online' if online else 'user_offline'
    # Find all conversations this user participates in
    memberships = ConversationMember.query.filter_by(user_id=user_id).all()
    notified = set()
    for m in memberships:
        others = ConversationMember.query.filter(
            ConversationMember.conversation_id == m.conversation_id,
            ConversationMember.user_id != user_id
        ).all()
        for other in others:
            if other.user_id not in notified:
                socketio.emit(event, {
                    'user_id': user_id,
                    'timestamp': datetime.utcnow().isoformat(),
                }, room=f'user_{other.user_id}')
                notified.add(other.user_id)
