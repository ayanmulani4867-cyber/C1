/**
 * Campus Connect Chat — Frontend JS
 * Handles Socket.IO real-time messaging, UI state, typing indicators,
 * online presence, file uploads, message actions, and notifications.
 *
 * All sender identity comes from server-side auth — never sent by client.
 */

'use strict';

// ── State ─────────────────────────────────────────────────────────────────────
const state = {
  currentUser: null,       // { id, name, avatar, role }
  conversations: [],       // All conversation objects
  activeConvId: null,      // Currently open conversation ID
  messages: {},            // { convId: [msg, ...] }
  onlineUsers: new Set(),  // Set of online user IDs
  typingTimers: {},        // { convId_userId: timeoutId }
  typingUsers: {},         // { convId: Set<userId> }
  pendingReply: null,      // message object being replied to
  pendingFiles: [],        // staged file attachments
  socket: null,
  hasMoreMessages: {},     // { convId: bool }
  loadingMessages: false,
  searchQuery: '',
  modalSelectedUsers: new Set(),
  modalSearchResults: [],
};

// ── DOM helpers ───────────────────────────────────────────────────────────────
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

function el(tag, cls, inner = '') {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (inner) e.innerHTML = inner;
  return e;
}

function formatTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  const now = new Date();
  const diffDays = (now - d) / 86400000;
  if (diffDays < 1 && d.getDate() === now.getDate()) {
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  if (diffDays < 7) {
    return d.toLocaleDateString([], { weekday: 'short' });
  }
  return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
}

function formatBytes(bytes) {
  if (!bytes) return '';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / 1048576).toFixed(1) + ' MB';
}

function avatarHtml(url, name, size = 44) {
  if (url && url.startsWith('http')) {
    return `<img src="${url}" alt="${esc(name)}" style="width:${size}px;height:${size}px;border-radius:50%;object-fit:cover">`;
  }
  const initials = (name || 'U').split(' ').slice(0, 2).map(s => s[0]).join('').toUpperCase();
  return `<div class="avatar-placeholder" style="width:${size}px;height:${size}px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:${Math.round(size*0.35)}px;color:#fff;background:linear-gradient(135deg,#4f46e5,#7c3aed)">${initials}</div>`;
}

function esc(str) {
  return String(str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function fileIcon(mime) {
  if (!mime) return '📄';
  if (mime.includes('pdf')) return '📕';
  if (mime.includes('word')) return '📘';
  if (mime.includes('sheet') || mime.includes('excel')) return '📗';
  if (mime.includes('presentation') || mime.includes('powerpoint')) return '📙';
  return '📄';
}

// ── Auth helpers ──────────────────────────────────────────────────────────────
function getAuthToken() {
  try {
    return sessionStorage.getItem('CAMPUS_CONNECT_ERP_token') || window._appAuthToken || '';
  } catch (e) {
    return window._appAuthToken || '';
  }
}

// ── API helpers ───────────────────────────────────────────────────────────────
async function apiFetch(url, opts = {}) {
  const token = getAuthToken();
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const resp = await fetch(url, {
    headers,
    ...opts,
  });
  return resp.json();
}

// ── Initialization ─────────────────────────────────────────────────────────────
async function init() {
  // Fetch current user info from meta tags embedded by server
  const meta = document.getElementById('chat-meta');
  if (!meta) return;
  state.currentUser = {
    id: parseInt(meta.dataset.userId),
    name: meta.dataset.userName,
    avatar: meta.dataset.userAvatar,
    role: meta.dataset.userRole,
  };

  await loadConversations();
  initSocket();
  renderSidebar();
  bindGlobalEvents();
  renderEmptyState();
}

// ── Socket.IO ────────────────────────────────────────────────────────────────
function initSocket() {
  const token = getAuthToken();
  const socketOpts = {
    transports: ['websocket', 'polling'],
  };
  if (token) {
    socketOpts.auth = { token };
    socketOpts.query = { token };
  }
  const s = state.socket = io(socketOpts);

  s.on('connect', () => {
    showBanner('');
    console.log('[Chat] Connected', s.id);
  });

  s.on('disconnect', () => {
    showBanner('disconnected', '⚡ Disconnected — reconnecting…');
  });

  s.on('connect_error', () => {
    showBanner('reconnecting', '⏳ Reconnecting to chat server…');
  });

  s.on('new_message', ({ message }) => {
    handleNewMessage(message);
  });

  s.on('message_deleted', ({ message_id }) => {
    handleMessageDeleted(message_id);
  });

  s.on('message_read', ({ conversation_id, reader_id, last_read_message_id }) => {
    handleReadReceipt(conversation_id, reader_id, last_read_message_id);
  });

  s.on('typing_start', ({ conversation_id, user_id, user_name }) => {
    handleTypingStart(conversation_id, user_id, user_name);
  });

  s.on('typing_stop', ({ conversation_id, user_id }) => {
    handleTypingStop(conversation_id, user_id);
  });

  s.on('user_online', ({ user_id }) => {
    state.onlineUsers.add(user_id);
    updatePresenceUI(user_id, true);
  });

  s.on('user_offline', ({ user_id }) => {
    state.onlineUsers.delete(user_id);
    updatePresenceUI(user_id, false);
  });

  s.on('conversation_updated', ({ action, conversation, user_id }) => {
    if (action === 'new_group' && conversation) {
      upsertConversation(conversation);
      renderSidebar();
    }
  });

  s.on('unread_count_updated', ({ conversation_id, unread_count }) => {
    updateUnreadBadge(conversation_id, unread_count);
  });
}

// ── Conversations ─────────────────────────────────────────────────────────────
async function loadConversations() {
  const data = await apiFetch('/api/chat/conversations');
  if (data.success) {
    state.conversations = data.conversations;
  }
}

function upsertConversation(conv) {
  const idx = state.conversations.findIndex(c => c.id === conv.id);
  if (idx >= 0) {
    state.conversations[idx] = conv;
  } else {
    state.conversations.unshift(conv);
  }
}

function getDisplayName(conv) {
  if (conv.is_group) return conv.title || 'Group Chat';
  if (conv.other_user) return conv.other_user.name;
  return 'Unknown';
}

function getDisplayAvatar(conv) {
  if (conv.is_group) return conv.avatar_url || null;
  if (conv.other_user) return conv.other_user.avatar;
  return null;
}

function getOtherUserId(conv) {
  if (!conv.is_group && conv.other_user) return conv.other_user.id;
  return null;
}

// ── Sidebar rendering ─────────────────────────────────────────────────────────
function renderSidebar() {
  const list = document.getElementById('conv-list');
  if (!list) return;

  const q = state.searchQuery.toLowerCase();
  let convs = state.conversations;
  if (q) {
    convs = convs.filter(c => getDisplayName(c).toLowerCase().includes(q));
  }

  // Sort: pinned first, then by updated_at
  convs = [...convs].sort((a, b) => {
    if (a.is_pinned && !b.is_pinned) return -1;
    if (!a.is_pinned && b.is_pinned) return 1;
    return new Date(b.updated_at || 0) - new Date(a.updated_at || 0);
  });

  if (convs.length === 0) {
    list.innerHTML = `<div class="chat-empty-state" style="padding:30px 20px"><p>No conversations yet. Start a new chat!</p></div>`;
    return;
  }

  list.innerHTML = convs.map(conv => {
    const name = getDisplayName(conv);
    const avatar = getDisplayAvatar(conv);
    const otherId = getOtherUserId(conv);
    const isOnline = otherId && state.onlineUsers.has(otherId);
    const unread = conv.unread_count || 0;
    const lastMsg = conv.last_message;
    let preview = '';
    if (lastMsg) {
      if (lastMsg.is_deleted) preview = 'Message deleted';
      else if (lastMsg.message_type === 'image') preview = '📷 Image';
      else if (lastMsg.message_type === 'file') preview = `📎 ${lastMsg.attachment_name || 'File'}`;
      else preview = lastMsg.content || '';
    }
    return `
      <div class="chat-conv-item ${state.activeConvId === conv.id ? 'active' : ''} ${conv.is_pinned ? 'pinned' : ''}"
           data-conv-id="${conv.id}" onclick="openConversation(${conv.id})">
        <div class="chat-conv-avatar">
          ${avatarHtml(avatar, name, 44)}
          ${!conv.is_group ? `<div class="online-dot${isOnline ? '' : ' offline'}"></div>` : ''}
        </div>
        <div class="chat-conv-info">
          <div class="chat-conv-name">${esc(name)}</div>
          <div class="chat-conv-preview ${unread ? 'unread' : ''}">${esc(preview)}</div>
        </div>
        <div class="chat-conv-meta">
          <div class="chat-conv-time">${lastMsg ? formatTime(lastMsg.created_at) : ''}</div>
          <div style="display:flex;gap:4px;align-items:center">
            ${unread ? `<div class="chat-unread-badge">${unread > 99 ? '99+' : unread}</div>` : ''}
            ${conv.is_muted ? '<span title="Muted">🔇</span>' : ''}
            ${conv.is_pinned ? '<span title="Pinned">📌</span>' : ''}
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// ── Open a conversation ───────────────────────────────────────────────────────
async function openConversation(convId) {
  state.activeConvId = convId;

  // On mobile: show main, hide sidebar
  document.querySelector('.chat-sidebar')?.classList.add('hidden');
  document.querySelector('.chat-main')?.classList.add('active');

  renderSidebar();
  renderChatHeader();
  renderMessages(true);

  // Join socket room
  if (state.socket) {
    state.socket.emit('join_conversation', { conversation_id: convId });
  }

  // Load messages
  await fetchMessages(convId, true);
  markAsRead(convId);
}

function getActiveConv() {
  return state.conversations.find(c => c.id === state.activeConvId);
}

// ── Chat header ────────────────────────────────────────────────────────────────
function renderChatHeader() {
  const conv = getActiveConv();
  const header = document.getElementById('chat-header');
  if (!header || !conv) return;

  const name = getDisplayName(conv);
  const avatar = getDisplayAvatar(conv);
  const otherId = getOtherUserId(conv);
  const isOnline = otherId && state.onlineUsers.has(otherId);

  let subtitle = '';
  if (conv.is_group) {
    const memberCount = conv.members?.length || '';
    subtitle = memberCount ? `${memberCount} members` : 'Group';
  } else {
    subtitle = isOnline ? 'Online' : 'Offline';
  }

  header.innerHTML = `
    <button class="chat-header-back" onclick="backToList()" title="Back">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
    </button>
    <div class="chat-header-avatar">${avatarHtml(avatar, name, 40)}</div>
    <div class="chat-header-info">
      <div class="chat-header-name">${esc(name)}</div>
      <div class="chat-header-status ${isOnline ? 'online' : ''}">${esc(subtitle)}</div>
    </div>
    <div class="chat-header-actions">
      <button class="chat-header-btn" onclick="openSearchPanel()" title="Search messages">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
      </button>
      ${conv.is_group ? `<button class="chat-header-btn" onclick="openGroupInfo()" title="Group info">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M6 20v-2a6 6 0 0 1 12 0v2"/></svg>
      </button>` : ''}
      <button class="chat-header-btn" onclick="openConvSettings()" title="Settings">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
      </button>
    </div>
  `;
}

// ── Messages ──────────────────────────────────────────────────────────────────
async function fetchMessages(convId, reset = false) {
  if (state.loadingMessages) return;
  state.loadingMessages = true;

  const existingMsgs = state.messages[convId] || [];
  let url = `/api/chat/conversations/${convId}/messages`;
  if (!reset && existingMsgs.length > 0) {
    url += `?before_id=${existingMsgs[0].id}`;
  }

  const data = await apiFetch(url);
  state.loadingMessages = false;

  if (!data.success) return;

  if (reset) {
    state.messages[convId] = data.messages;
  } else {
    state.messages[convId] = [...data.messages, ...existingMsgs];
  }
  state.hasMoreMessages[convId] = data.has_more;

  renderMessages(reset);
}

function renderMessages(scrollToBottom = false) {
  const convId = state.activeConvId;
  const container = document.getElementById('chat-messages');
  if (!container || !convId) return;

  const msgs = state.messages[convId] || [];
  const hasMore = state.hasMoreMessages[convId];

  let html = '';

  if (hasMore) {
    html += `<div class="chat-load-more"><button class="chat-load-more-btn" onclick="loadOlderMessages()">Load older messages</button></div>`;
  }

  let lastDate = null;
  for (const msg of msgs) {
    const d = new Date(msg.created_at);
    const dateStr = d.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' });
    if (dateStr !== lastDate) {
      html += `<div class="chat-date-divider">${esc(dateStr)}</div>`;
      lastDate = dateStr;
    }
    html += renderMessageRow(msg);
  }

  container.innerHTML = html;
  if (scrollToBottom) {
    container.scrollTop = container.scrollHeight;
  }
}

function renderMessageRow(msg) {
  const isMe = msg.sender_id === state.currentUser?.id;
  const sender = msg.sender || {};
  const senderName = sender.name || 'Unknown';
  const senderAvatar = sender.avatar || '';
  const time = formatTime(msg.created_at);

  let bubbleContent = '';

  if (msg.is_deleted) {
    bubbleContent = `<span style="font-style:italic;opacity:0.55">🚫 Message deleted</span>`;
  } else {
    // Reply preview
    if (msg.reply_to) {
      const rt = msg.reply_to;
      let rtPreview = rt.content || '';
      if (rt.message_type === 'image') rtPreview = '📷 Image';
      else if (rt.message_type === 'file') rtPreview = `📎 ${rt.attachment_name || 'File'}`;
      bubbleContent += `
        <div class="chat-bubble-reply">
          <div class="chat-bubble-reply-name">${esc(rt.sender_name || 'User')}</div>
          <div class="chat-bubble-reply-text">${esc(rtPreview)}</div>
        </div>`;
    }

    if (msg.message_type === 'image' && msg.attachment_url) {
      bubbleContent += `<img class="chat-bubble-img" src="${esc(msg.attachment_url)}" alt="${esc(msg.attachment_name || 'Image')}" onclick="openLightbox('${esc(msg.attachment_url)}')">`;
      if (msg.content) bubbleContent += `<div style="margin-top:6px">${esc(msg.content)}</div>`;
    } else if (msg.message_type === 'file' && msg.attachment_url) {
      bubbleContent += `
        <a class="chat-bubble-file" href="${esc(msg.attachment_url)}" target="_blank" download="${esc(msg.attachment_name || 'file')}">
          <span class="chat-bubble-file-icon">${fileIcon(msg.attachment_mime)}</span>
          <div class="chat-bubble-file-info">
            <div class="chat-bubble-file-name">${esc(msg.attachment_name || 'File')}</div>
            <div class="chat-bubble-file-size">${formatBytes(msg.attachment_size)}</div>
          </div>
        </a>`;
    } else {
      bubbleContent += esc(msg.content || '');
    }
  }

  // Read status icons (for own messages)
  let statusIcon = '';
  if (isMe) {
    const readBy = msg.read_by || [];
    const delivered = readBy.length > 0;
    if (delivered) {
      statusIcon = `<span class="chat-msg-status status-read" title="Read">✓✓</span>`;
    } else {
      statusIcon = `<span class="chat-msg-status status-sent" title="Sent">✓</span>`;
    }
  }

  const conv = getActiveConv();
  const showName = conv?.is_group && !isMe;

  return `
    <div class="chat-msg-row ${isMe ? 'mine' : 'theirs'}" data-msg-id="${msg.id}"
         oncontextmenu="showContextMenu(event, ${msg.id}, ${isMe})">
      ${!isMe ? `<div class="chat-msg-avatar">${avatarHtml(senderAvatar, senderName, 30)}</div>` : ''}
      <div class="chat-msg-body">
        ${showName ? `<div class="chat-msg-sender-name">${esc(senderName)}</div>` : ''}
        <div class="chat-bubble ${msg.is_deleted ? 'deleted' : ''}">${bubbleContent}</div>
        <div class="chat-msg-meta">
          <span class="chat-conv-time">${esc(time)}</span>
          ${statusIcon}
        </div>
      </div>
      ${isMe ? `<div class="chat-msg-avatar">${avatarHtml(senderAvatar, senderName, 30)}</div>` : ''}
    </div>
  `;
}

async function loadOlderMessages() {
  await fetchMessages(state.activeConvId, false);
}

// ── Handle incoming message ───────────────────────────────────────────────────
function handleNewMessage(msg) {
  const convId = msg.conversation_id;
  if (!state.messages[convId]) state.messages[convId] = [];
  state.messages[convId].push(msg);

  // Update last message in conversations
  const conv = state.conversations.find(c => c.id === convId);
  if (conv) {
    conv.last_message = msg;
    conv.updated_at = msg.created_at;
    if (convId !== state.activeConvId) {
      conv.unread_count = (conv.unread_count || 0) + 1;
    }
  }

  if (convId === state.activeConvId) {
    const container = document.getElementById('chat-messages');
    if (container) {
      const row = el('div');
      row.innerHTML = renderMessageRow(msg);
      container.appendChild(row.firstElementChild);
      container.scrollTop = container.scrollHeight;
    }
    if (convId === state.activeConvId) {
      markAsRead(convId);
    }
  } else {
    // Show toast notification for background conversation
    showToast(msg);
  }

  renderSidebar();

  // Notify message delivered to sender
  if (msg.sender_id !== state.currentUser?.id && state.socket) {
    state.socket.emit('message_delivered', { message_id: msg.id });
  }
}

function handleMessageDeleted(msgId) {
  for (const convId in state.messages) {
    const idx = state.messages[convId].findIndex(m => m.id === msgId);
    if (idx >= 0) {
      state.messages[convId][idx].is_deleted = true;
      state.messages[convId][idx].content = null;
    }
  }
  if (state.activeConvId) {
    const row = document.querySelector(`[data-msg-id="${msgId}"]`);
    if (row) {
      const bubble = row.querySelector('.chat-bubble');
      if (bubble) {
        bubble.classList.add('deleted');
        bubble.innerHTML = `<span style="font-style:italic;opacity:0.55">🚫 Message deleted</span>`;
      }
    }
  }
}

function handleReadReceipt(convId, readerId, lastMsgId) {
  // Update read_by for all messages up to lastMsgId in this conv
  const msgs = state.messages[convId] || [];
  for (const msg of msgs) {
    if (msg.id <= lastMsgId && !msg.read_by?.includes(readerId)) {
      msg.read_by = [...(msg.read_by || []), readerId];
    }
  }
  if (convId === state.activeConvId) {
    // Re-render status icons
    renderMessages(false);
  }
}

// ── Mark as read ───────────────────────────────────────────────────────────────
async function markAsRead(convId) {
  await apiFetch(`/api/chat/conversations/${convId}/read`, { method: 'POST' });
  const conv = state.conversations.find(c => c.id === convId);
  if (conv) conv.unread_count = 0;
  renderSidebar();
}

// ── Sending messages ─────────────────────────────────────────────────────────
async function sendMessage() {
  const convId = state.activeConvId;
  if (!convId) return;

  const textarea = document.getElementById('chat-textarea');
  const content = textarea?.value.trim();

  if (state.pendingFiles.length > 0) {
    await sendFiles(convId);
  }

  if (!content) return;

  textarea.value = '';
  autoResize(textarea);

  const body = { content, message_type: 'text' };
  if (state.pendingReply) {
    body.reply_to_id = state.pendingReply.id;
    clearReply();
  }

  // Optimistic: send immediately
  const data = await apiFetch(`/api/chat/conversations/${convId}/messages`, {
    method: 'POST',
    body: JSON.stringify(body),
  });

  if (!data.success) {
    showErrorToast(data.message || 'Failed to send message');
  }
}

async function sendFiles(convId) {
  const token = getAuthToken();
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  for (const file of state.pendingFiles) {
    const formData = new FormData();
    formData.append('file', file);
    if (state.pendingReply) {
      formData.append('reply_to_id', state.pendingReply.id);
    }
    const resp = await fetch(`/api/chat/conversations/${convId}/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });
    const data = await resp.json();
    if (!data.success) {
      showErrorToast(data.message || 'File upload failed');
    }
  }
  state.pendingFiles = [];
  clearReply();
  renderAttachPreviews();
}

// ── Typing indicator ──────────────────────────────────────────────────────────
let _typingTimeout = null;

function handleTextareaInput(e) {
  autoResize(e.target);
  const convId = state.activeConvId;
  if (!convId || !state.socket) return;

  state.socket.emit('typing_start', { conversation_id: convId });

  if (_typingTimeout) clearTimeout(_typingTimeout);
  _typingTimeout = setTimeout(() => {
    state.socket.emit('typing_stop', { conversation_id: convId });
  }, 1500);
}

function handleTypingStart(convId, userId, userName) {
  if (userId === state.currentUser?.id) return;
  if (!state.typingUsers[convId]) state.typingUsers[convId] = new Set();
  state.typingUsers[convId].add(userId);
  if (state.typingTimers[`${convId}_${userId}`]) clearTimeout(state.typingTimers[`${convId}_${userId}`]);
  state.typingTimers[`${convId}_${userId}`] = setTimeout(() => {
    handleTypingStop(convId, userId);
  }, 3000);
  if (convId === state.activeConvId) renderTypingBar();
}

function handleTypingStop(convId, userId) {
  if (state.typingUsers[convId]) {
    state.typingUsers[convId].delete(userId);
  }
  if (convId === state.activeConvId) renderTypingBar();
}

function renderTypingBar() {
  const bar = document.getElementById('typing-bar');
  if (!bar) return;
  const convId = state.activeConvId;
  const typers = convId ? [...(state.typingUsers[convId] || [])] : [];
  if (typers.length === 0) {
    bar.innerHTML = '';
    return;
  }
  const conv = getActiveConv();
  // Get names from recent messages
  const names = typers.slice(0, 2).map(uid => {
    const msgs = state.messages[convId] || [];
    const msg = [...msgs].reverse().find(m => m.sender_id === uid);
    return msg?.sender?.name || 'Someone';
  });
  const label = names.length === 1 ? `${names[0]} is typing` : `${names.join(' & ')} are typing`;
  bar.innerHTML = `<span class="typing-dots"><span></span><span></span><span></span></span>${esc(label)}…`;
}

// ── Presence ──────────────────────────────────────────────────────────────────
function updatePresenceUI(userId, online) {
  // Update sidebar dots
  $$('.chat-conv-item').forEach(item => {
    const convId = parseInt(item.dataset.convId);
    const conv = state.conversations.find(c => c.id === convId);
    if (conv && !conv.is_group && conv.other_user?.id === userId) {
      const dot = item.querySelector('.online-dot');
      if (dot) dot.className = `online-dot${online ? '' : ' offline'}`;
    }
  });

  // Update header
  if (state.activeConvId) {
    const conv = getActiveConv();
    if (conv && !conv.is_group && conv.other_user?.id === userId) {
      const statusEl = document.querySelector('.chat-header-status');
      if (statusEl) {
        statusEl.textContent = online ? 'Online' : 'Offline';
        statusEl.className = `chat-header-status${online ? ' online' : ''}`;
      }
    }
  }
}

function updateUnreadBadge(convId, count) {
  const conv = state.conversations.find(c => c.id === convId);
  if (conv) conv.unread_count = count;
  renderSidebar();
}

// ── Context menu (right-click / long-press) ────────────────────────────────────
let _ctxMenu = null;

function showContextMenu(e, msgId, isMe) {
  e.preventDefault();
  closeContextMenu();

  const msg = findMessage(msgId);
  if (!msg || msg.is_deleted) return;

  const menu = el('div', 'chat-ctx-menu');
  menu.innerHTML = `
    <div class="chat-ctx-item" onclick="replyToMessage(${msgId})">
      <span>↩️</span> Reply
    </div>
    <div class="chat-ctx-item" onclick="copyMessage(${msgId})">
      <span>📋</span> Copy
    </div>
    ${isMe ? `<div class="chat-ctx-item danger" onclick="deleteMessage(${msgId})">🗑️ Delete</div>` : `<div class="chat-ctx-item danger" onclick="reportMessage(${msgId})">🚩 Report</div>`}
  `;

  const x = Math.min(e.clientX, window.innerWidth - 180);
  const y = Math.min(e.clientY, window.innerHeight - 150);
  menu.style.left = x + 'px';
  menu.style.top = y + 'px';
  document.body.appendChild(menu);
  _ctxMenu = menu;

  setTimeout(() => document.addEventListener('click', closeContextMenu, { once: true }), 10);
}

function closeContextMenu() {
  if (_ctxMenu) { _ctxMenu.remove(); _ctxMenu = null; }
}

function findMessage(msgId) {
  for (const convId in state.messages) {
    const msg = state.messages[convId].find(m => m.id === msgId);
    if (msg) return msg;
  }
  return null;
}

function replyToMessage(msgId) {
  const msg = findMessage(msgId);
  if (!msg) return;
  state.pendingReply = msg;
  renderReplyBar();
  document.getElementById('chat-textarea')?.focus();
}

function clearReply() {
  state.pendingReply = null;
  renderReplyBar();
}

function renderReplyBar() {
  const bar = document.getElementById('reply-preview');
  if (!bar) return;
  if (!state.pendingReply) { bar.innerHTML = ''; return; }
  const msg = state.pendingReply;
  let preview = msg.content || '';
  if (msg.message_type === 'image') preview = '📷 Image';
  else if (msg.message_type === 'file') preview = `📎 ${msg.attachment_name || 'File'}`;
  bar.innerHTML = `
    <div class="chat-reply-preview">
      <span>↩️</span>
      <div>
        <div class="reply-name">${esc(msg.sender?.name || 'User')}</div>
        <div>${esc(preview)}</div>
      </div>
      <div class="reply-close" onclick="clearReply()">✕</div>
    </div>
  `;
}

function copyMessage(msgId) {
  const msg = findMessage(msgId);
  if (msg?.content) navigator.clipboard.writeText(msg.content);
}

async function deleteMessage(msgId) {
  if (!confirm('Delete this message?')) return;
  const data = await apiFetch(`/api/chat/messages/${msgId}/delete`, { method: 'POST' });
  if (!data.success) showErrorToast(data.message || 'Failed to delete');
}

function reportMessage(msgId) {
  showReportModal(msgId);
}

// ── File handling ─────────────────────────────────────────────────────────────
function handleFileSelect(e) {
  const files = [...(e.target.files || [])];
  e.target.value = '';

  const ALLOWED = ['jpg','jpeg','png','webp','pdf','doc','docx','xls','xlsx','ppt','pptx'];
  const MAX = 10 * 1024 * 1024;
  const valid = files.filter(f => {
    const ext = f.name.split('.').pop().toLowerCase();
    if (!ALLOWED.includes(ext)) { showErrorToast(`${f.name}: unsupported type`); return false; }
    if (f.size > MAX) { showErrorToast(`${f.name}: exceeds 10 MB`); return false; }
    return true;
  });

  state.pendingFiles.push(...valid);
  renderAttachPreviews();
}

function renderAttachPreviews() {
  const strip = document.getElementById('attach-strip');
  if (!strip) return;
  if (state.pendingFiles.length === 0) { strip.innerHTML = ''; return; }
  strip.innerHTML = state.pendingFiles.map((f, i) => {
    const isImg = f.type.startsWith('image/');
    if (isImg) {
      const url = URL.createObjectURL(f);
      return `<div class="chat-attach-thumb"><img src="${url}" alt="${esc(f.name)}"><button class="chat-attach-thumb-rm" onclick="removePendingFile(${i})">✕</button></div>`;
    }
    return `<div class="chat-attach-thumb" style="display:flex;align-items:center;justify-content:center;font-size:22px">${fileIcon(f.type)}<button class="chat-attach-thumb-rm" onclick="removePendingFile(${i})">✕</button></div>`;
  }).join('');
}

function removePendingFile(i) {
  state.pendingFiles.splice(i, 1);
  renderAttachPreviews();
}

// ── Lightbox ──────────────────────────────────────────────────────────────────
function openLightbox(src) {
  const lb = el('div', 'chat-lightbox');
  lb.innerHTML = `<img src="${esc(src)}" alt="Full size image">`;
  lb.onclick = () => lb.remove();
  document.body.appendChild(lb);
}

// ── New Chat / Group modal ─────────────────────────────────────────────────────
function openNewChatModal() {
  state.modalSelectedUsers.clear();
  state.modalSearchResults = [];
  showModal({
    title: 'New Conversation',
    isGroup: false,
    onConfirm: async () => {
      const [uid] = [...state.modalSelectedUsers];
      if (!uid) return showErrorToast('Select a user first');
      const data = await apiFetch('/api/chat/conversations', {
        method: 'POST',
        body: JSON.stringify({ type: 'private', member_ids: [uid] }),
      });
      if (data.success) {
        upsertConversation(data.conversation);
        renderSidebar();
        openConversation(data.conversation.id);
      } else {
        showErrorToast(data.message);
      }
    },
  });
}

function openNewGroupModal() {
  state.modalSelectedUsers.clear();
  state.modalSearchResults = [];
  showModal({
    title: 'New Group Chat',
    isGroup: true,
    onConfirm: async () => {
      const members = [...state.modalSelectedUsers];
      if (members.length < 1) return showErrorToast('Add at least one member');
      const title = document.getElementById('modal-group-title')?.value.trim();
      if (!title) return showErrorToast('Group name required');
      const data = await apiFetch('/api/chat/conversations', {
        method: 'POST',
        body: JSON.stringify({ type: 'group', title, member_ids: members }),
      });
      if (data.success) {
        upsertConversation(data.conversation);
        renderSidebar();
        openConversation(data.conversation.id);
      } else {
        showErrorToast(data.message);
      }
    },
  });
}

function showModal({ title, isGroup, onConfirm }) {
  const overlay = el('div', 'chat-modal-overlay');
  overlay.id = 'chat-modal';
  overlay.innerHTML = `
    <div class="chat-modal">
      <div class="chat-modal-title">${esc(title)}</div>
      ${isGroup ? `<input id="modal-group-title" class="chat-modal-search" placeholder="Group name…">` : ''}
      <input id="modal-search" class="chat-modal-search" placeholder="Search users by name or email…">
      <div id="modal-results" class="chat-modal-results"></div>
      <div class="chat-modal-actions">
        <button class="chat-btn chat-btn-secondary" onclick="closeModal()">Cancel</button>
        <button class="chat-btn chat-btn-primary" id="modal-confirm">Start Chat</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  let searchTimer = null;
  document.getElementById('modal-search').addEventListener('input', e => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => doModalSearch(e.target.value, isGroup), 300);
  });

  document.getElementById('modal-confirm').addEventListener('click', onConfirm);
  overlay.addEventListener('click', e => { if (e.target === overlay) closeModal(); });
}

async function doModalSearch(q, isGroup) {
  if (q.length < 1) { document.getElementById('modal-results').innerHTML = ''; return; }
  const data = await apiFetch(`/api/chat/users/search?q=${encodeURIComponent(q)}`);
  const results = document.getElementById('modal-results');
  if (!data.success || !data.users?.length) {
    results.innerHTML = `<div class="text-muted" style="padding:12px">No users found</div>`;
    return;
  }
  results.innerHTML = data.users.map(u => {
    const sel = state.modalSelectedUsers.has(u.id);
    return `
      <div class="chat-user-result ${sel ? 'selected' : ''}" onclick="toggleModalUser(${u.id}, '${esc(u.name)}')">
        ${avatarHtml(u.avatar, u.name, 38)}
        <div class="chat-user-info">
          <div class="chat-user-name">${esc(u.name)}</div>
          <div class="chat-user-role">${esc(u.role)} ${u.department ? '• ' + esc(u.department) : ''}</div>
        </div>
        ${sel ? '<span>✓</span>' : ''}
      </div>
    `;
  }).join('');
}

function toggleModalUser(uid, name) {
  const conv = getActiveConv();
  if (state.modalSelectedUsers.has(uid)) {
    state.modalSelectedUsers.delete(uid);
  } else {
    state.modalSelectedUsers.add(uid);
  }
  // Re-render search
  const searchInput = document.getElementById('modal-search');
  if (searchInput) doModalSearch(searchInput.value, false);
}

function closeModal() {
  document.getElementById('chat-modal')?.remove();
}

// ── Report modal ──────────────────────────────────────────────────────────────
function showReportModal(msgId) {
  const overlay = el('div', 'chat-modal-overlay');
  overlay.id = 'report-modal';
  const reasons = [
    { value: 'spam', label: '🚫 Spam' },
    { value: 'harassment', label: '😡 Harassment' },
    { value: 'inappropriate', label: '⚠️ Inappropriate content' },
    { value: 'other', label: '📋 Other' },
  ];
  overlay.innerHTML = `
    <div class="chat-modal">
      <div class="chat-modal-title">Report Message</div>
      <div class="chat-report-options">
        ${reasons.map(r => `
          <div class="chat-report-option" onclick="selectReport('${r.value}')">
            <input type="radio" name="report-reason" value="${r.value}" id="rr-${r.value}">
            <label for="rr-${r.value}">${r.label}</label>
          </div>
        `).join('')}
      </div>
      <div class="chat-modal-actions">
        <button class="chat-btn chat-btn-secondary" onclick="document.getElementById('report-modal').remove()">Cancel</button>
        <button class="chat-btn chat-btn-primary" onclick="submitReport(${msgId})">Submit Report</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);
  overlay.addEventListener('click', e => { if (e.target === overlay) overlay.remove(); });
}

function selectReport(val) {
  $$('.chat-report-option').forEach(o => o.classList.remove('selected'));
  document.querySelector(`.chat-report-option:has(input[value="${val}"])`)?.classList.add('selected');
  document.querySelector(`input[name="report-reason"][value="${val}"]`).checked = true;
}

async function submitReport(msgId) {
  const reason = document.querySelector('input[name="report-reason"]:checked')?.value;
  if (!reason) return showErrorToast('Select a reason');
  const data = await apiFetch(`/api/chat/messages/${msgId}/report`, {
    method: 'POST',
    body: JSON.stringify({ reason }),
  });
  document.getElementById('report-modal')?.remove();
  if (data.success) showErrorToast('✅ Report submitted', false);
  else showErrorToast(data.message || 'Failed to report');
}

// ── Toast notifications ────────────────────────────────────────────────────────
function showToast(msg) {
  const sender = msg.sender || {};
  let preview = msg.content || '';
  if (msg.message_type === 'image') preview = '📷 Image';
  else if (msg.message_type === 'file') preview = `📎 ${msg.attachment_name || 'File'}`;

  const toast = el('div', 'chat-toast');
  toast.innerHTML = `
    <div class="chat-toast-avatar">${avatarHtml(sender.avatar, sender.name || 'User', 36)}</div>
    <div>
      <div class="chat-toast-title">${esc(sender.name || 'New message')}</div>
      <div class="chat-toast-body">${esc(preview.substring(0, 80))}</div>
    </div>
  `;
  toast.onclick = () => { toast.remove(); openConversation(msg.conversation_id); };
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 5000);

  // Browser Notification API
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(`${sender.name || 'New message'}`, {
      body: preview.substring(0, 100),
      icon: sender.avatar || '/static/icons/icon-192x192.png',
      tag: `chat-${msg.conversation_id}`,
    });
  }
}

function showErrorToast(msg, isError = true) {
  const toast = el('div', 'chat-toast');
  toast.style.borderColor = isError ? '#ef4444' : '#22c55e';
  toast.innerHTML = `<div class="chat-toast-title" style="color:${isError ? '#ef4444' : '#22c55e'}">${esc(msg)}</div>`;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}

// ── Connection banner ──────────────────────────────────────────────────────────
function showBanner(type, msg = '') {
  const banner = document.getElementById('conn-banner');
  if (!banner) return;
  if (!type) {
    banner.classList.remove('show');
    return;
  }
  banner.textContent = msg;
  banner.className = `chat-conn-banner ${type} show`;
}

// ── Conversation settings ─────────────────────────────────────────────────────
function openConvSettings() {
  const conv = getActiveConv();
  if (!conv) return;
  const overlay = el('div', 'chat-modal-overlay');
  overlay.id = 'settings-modal';
  overlay.innerHTML = `
    <div class="chat-modal">
      <div class="chat-modal-title">Conversation Settings</div>
      <div style="display:flex;flex-direction:column;gap:10px;margin-bottom:16px">
        <div class="chat-report-option" onclick="toggleSetting('mute', ${conv.id}, ${!conv.is_muted})">
          <span>${conv.is_muted ? '🔔 Unmute' : '🔇 Mute'} conversation</span>
        </div>
        <div class="chat-report-option" onclick="toggleSetting('pin', ${conv.id}, ${!conv.is_pinned})">
          <span>${conv.is_pinned ? '📌 Unpin' : '📌 Pin'} conversation</span>
        </div>
        <div class="chat-report-option" onclick="toggleSetting('archive', ${conv.id}, ${!conv.is_archived})">
          <span>${conv.is_archived ? '📤 Unarchive' : '📥 Archive'} conversation</span>
        </div>
      </div>
      <div class="chat-modal-actions">
        <button class="chat-btn chat-btn-secondary" onclick="document.getElementById('settings-modal').remove()">Close</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);
  overlay.addEventListener('click', e => { if (e.target === overlay) overlay.remove(); });
}

async function toggleSetting(setting, convId, value) {
  const body = {};
  if (setting === 'mute') body.is_muted = value;
  if (setting === 'pin') body.is_pinned = value;
  if (setting === 'archive') body.is_archived = value;
  await apiFetch(`/api/chat/conversations/${convId}/settings`, {
    method: 'PATCH',
    body: JSON.stringify(body),
  });
  const conv = state.conversations.find(c => c.id === convId);
  if (conv) Object.assign(conv, body);
  document.getElementById('settings-modal')?.remove();
  renderSidebar();
}

// ── Search panel ───────────────────────────────────────────────────────────────
function openSearchPanel() {
  const q = prompt('Search in conversation:');
  if (!q) return;
  searchMessages(q);
}

async function searchMessages(q) {
  const convId = state.activeConvId;
  if (!convId) return;
  const data = await apiFetch(`/api/chat/conversations/${convId}/messages?q=${encodeURIComponent(q)}`);
  if (data.success) {
    state.messages[convId] = data.messages;
    renderMessages(true);
  }
}

// ── Back button (mobile) ────────────────────────────────────────────────────────
function backToList() {
  document.querySelector('.chat-sidebar')?.classList.remove('hidden');
  document.querySelector('.chat-main')?.classList.remove('active');
  state.activeConvId = null;
}

// ── Empty state ────────────────────────────────────────────────────────────────
function renderEmptyState() {
  const mainArea = document.getElementById('chat-area');
  if (!mainArea || state.activeConvId) return;
  mainArea.innerHTML = `
    <div class="chat-empty-state">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
      <h3>Welcome to SITCOE Chat</h3>
      <p>Select a conversation or start a new chat with students, faculty, or HOD.</p>
    </div>
  `;
}

// ── Auto resize textarea ───────────────────────────────────────────────────────
function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

// ── Global event bindings ──────────────────────────────────────────────────────
function bindGlobalEvents() {
  // Search sidebar
  document.getElementById('sidebar-search')?.addEventListener('input', e => {
    state.searchQuery = e.target.value;
    renderSidebar();
  });

  // Textarea
  const ta = document.getElementById('chat-textarea');
  if (ta) {
    ta.addEventListener('input', handleTextareaInput);
    ta.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  // Request notification permission
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
  }

  // Infinite scroll (load older messages)
  const msgContainer = document.getElementById('chat-messages');
  if (msgContainer) {
    msgContainer.addEventListener('scroll', () => {
      if (msgContainer.scrollTop === 0 && state.hasMoreMessages[state.activeConvId]) {
        loadOlderMessages();
      }
    });
  }
}

// ── Init on DOMContentLoaded ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', init);
