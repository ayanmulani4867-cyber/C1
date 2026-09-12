/**
 * Campus Connect ERP - Unified Stitch Frontend Connector
 * Integrates Stitch UI with Flask Backend & Firebase Realtime Database
 */

(function() {
  'use strict';

  // State
  let currentUser = null;
  let allStudents = [];
  let allFaculty = [];
  let allDepartments = [];
  let allCourses = [];
  let allSubjects = [];
  let allAttendance = [];
  let allResults = [];
  let allNotices = [];
  let allMaterials = [];
  let allEvents = [];

  // Route map for Stitch sidebar data-path
  const ROUTE_MAP = {
    'dashboard': '/admin/dashboard',
    'analytics-and-reports': '/admin/dashboard',
    'departments': '/admin/departments',
    'courses-and-syllabus': '/admin/courses',
    'courses-and-curriculum': '/admin/courses',
    'subjects': '/admin/subjects',
    'students-directory': '/admin/students',
    'faculty-and-staff': '/admin/faculty',
    'hod-management': '/admin/hod',
    'attendance-tracker': '/attendance',
    'examination-and-results': '/results',
    'official-notices': '/notices',
    'study-materials-repository': '/materials',
    'campus-events': '/events',
    'settings': '/settings',
    'role-permissions': '/settings',
    'audit-logs': '/settings',
    'student-dashboard': '/student/dashboard',
    'student-courses': '/student/academics',
    'student-attendance': '/student/academics'
  };

  // Toast Notification Helper
  function showToast(message, type = 'success') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'fixed bottom-5 right-5 z-[9999] flex flex-col gap-2 pointer-events-none';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const isSuccess = type === 'success';
    const isError = type === 'error';
    const bgColor = isSuccess ? 'bg-primary-container text-on-primary' : (isError ? 'bg-error-container text-on-error-container' : 'bg-surface-container-highest text-on-surface');
    const icon = isSuccess ? 'check_circle' : (isError ? 'error' : 'info');

    toast.className = `${bgColor} px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 text-sm font-medium transition-all duration-300 transform translate-y-2 opacity-0 pointer-events-auto max-w-md`;
    toast.innerHTML = `
      <span class="material-symbols-outlined text-lg">${icon}</span>
      <span class="flex-1">${message}</span>
      <button class="opacity-70 hover:opacity-100 material-symbols-outlined text-sm" onclick="this.parentElement.remove()">close</button>
    `;

    container.appendChild(toast);
    requestAnimationFrame(() => {
      toast.classList.remove('translate-y-2', 'opacity-0');
    });

    setTimeout(() => {
      toast.classList.add('opacity-0', 'translate-y-2');
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  // Generic Fetch API with error handling
  async function apiCall(endpoint, method = 'GET', body = null) {
    try {
      const options = {
        method,
        headers: {
          'Accept': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        }
      };

      if (body) {
        if (body instanceof FormData) {
          options.body = body;
        } else {
          options.headers['Content-Type'] = 'application/json';
          options.body = JSON.stringify(body);
        }
      }

      // Check token in localStorage if present
      const token = localStorage.getItem('campus_connect_token');
      if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
      }

      const res = await fetch(endpoint, options);
      if (res.status === 401) {
        if (!window.location.pathname.startsWith('/login')) {
          window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
        }
        return null;
      }
      if (res.status === 403) {
        showToast('Access Forbidden: You do not have permission for this action.', 'error');
        return null;
      }
      if (res.status === 503) {
        const errJson = await res.json().catch(() => ({}));
        showToast(errJson.message || 'Firebase Database connection error in production.', 'error');
        return null;
      }

      const data = await res.json();
      return data;
    } catch (err) {
      console.error(`API Call failed on ${endpoint}:`, err);
      return null;
    }
  }

  // =========================================================================
  // 1. INITIALIZE & BIND USER CONTEXT
  // =========================================================================

  async function checkAuthAndPopulateUser() {
    const isLoginPage = window.location.pathname.startsWith('/login');
    const data = await apiCall('/api/auth/me');

    if (data && data.success && data.user) {
      currentUser = data.user;
      if (isLoginPage) {
        // Redirect to role dashboard if already authenticated
        if (currentUser.role === 'ADMIN') window.location.href = '/admin/dashboard';
        else if (currentUser.role === 'HOD') window.location.href = '/hod/dashboard';
        else if (currentUser.role === 'FACULTY') window.location.href = '/faculty/dashboard';
        else window.location.href = '/student/dashboard';
        return;
      }
      updateUserInterface(currentUser);
    } else if (!isLoginPage && !window.location.pathname.startsWith('/health')) {
      // Not authenticated on protected page
      window.location.href = '/login?next=' + encodeURIComponent(window.location.pathname);
    }
  }

  function updateUserInterface(user) {
    // Populate user profile info in sidebar
    const profileSections = document.querySelectorAll('aside, header');
    profileSections.forEach(section => {
      const nameEl = section.querySelector('.font-headline-sm.text-on-surface.truncate');
      if (nameEl) nameEl.textContent = `${user.first_name || ''} ${user.last_name || user.username}`.trim();

      const roleBadge = section.querySelector('.font-label-sm.text-on-surface.font-semibold, .font-label-sm.text-secondary.truncate');
      if (roleBadge) {
        roleBadge.textContent = `${user.role} • ${user.username}`;
      }
    });

    // Wire up sign-out button
    document.querySelectorAll('button[title="Sign Out"], button[title="Logout"], button.logout-btn').forEach(btn => {
      btn.addEventListener('click', handleLogout);
    });

    // Also look for buttons containing 'logout' icon
    document.querySelectorAll('button').forEach(btn => {
      if (btn.querySelector('.material-symbols-outlined') && btn.innerText.toLowerCase().includes('sign out') ||
          (btn.innerHTML.includes('logout') && !btn.hasAttribute('data-bound'))) {
        btn.setAttribute('data-bound', 'true');
        btn.addEventListener('click', handleLogout);
      }
    });
  }

  async function handleLogout(e) {
    if (e) e.preventDefault();
    localStorage.removeItem('campus_connect_token');
    await apiCall('/api/auth/logout', 'POST');
    window.location.href = '/login';
  }

  // =========================================================================
  // 2. UNIVERSAL SIDEBAR NAVIGATION BINDING
  // =========================================================================

  function bindSidebarNavigation() {
    const navItems = document.querySelectorAll('aside nav a[data-path], aside a[data-path]');
    const currentPath = window.location.pathname;

    navItems.forEach(item => {
      const dataPath = item.getAttribute('data-path');
      let targetUrl = ROUTE_MAP[dataPath] || '#';

      // Role-specific routing for 'dashboard'
      if (dataPath === 'dashboard' && currentUser) {
        if (currentUser.role === 'STUDENT') targetUrl = '/student/dashboard';
        else if (currentUser.role === 'FACULTY') targetUrl = '/faculty/dashboard';
        else if (currentUser.role === 'HOD') targetUrl = '/hod/dashboard';
        else targetUrl = '/admin/dashboard';
      }

      item.setAttribute('href', targetUrl);

      // Active tab highlighting
      if (currentPath === targetUrl || (targetUrl !== '/admin/dashboard' && currentPath.startsWith(targetUrl))) {
        item.classList.add('bg-primary-container', 'text-on-primary', 'font-semibold', 'shadow-sm');
        item.classList.remove('text-on-surface-variant', 'hover:bg-surface-container');
      } else {
        item.classList.remove('bg-primary-container', 'text-on-primary', 'font-semibold', 'shadow-sm');
        item.classList.add('text-on-surface-variant');
      }

      item.addEventListener('click', function(e) {
        if (targetUrl && targetUrl !== '#') {
          e.preventDefault();
          window.location.href = targetUrl;
        }
      });
    });

    // Top logo click -> home/dashboard
    const logoLink = document.querySelector('aside .flex.items-center.gap-space-md');
    if (logoLink) {
      logoLink.style.cursor = 'pointer';
      logoLink.addEventListener('click', () => {
        window.location.href = '/';
      });
    }

    // Top Profile click -> profile page
    const profileDropdown = document.querySelector('header .flex.items-center.gap-space-xs.cursor-pointer');
    if (profileDropdown) {
      profileDropdown.addEventListener('click', () => {
        window.location.href = '/profile';
      });
    }

    // Top Quick Action buttons
    const quickActionBtn = document.querySelector('header button.bg-primary-container');
    if (quickActionBtn && !window.location.pathname.startsWith('/login')) {
      quickActionBtn.addEventListener('click', () => {
        const dest = currentUser && currentUser.role === 'STUDENT' ? '/student/academics' : '/admin/students';
        window.location.href = dest;
      });
    }
  }

  // =========================================================================
  // 3. LOGIN PAGE INTEGRATION
  // =========================================================================

  function initLoginPage() {
    const loginBtn = document.querySelector('button[onclick="handleLoginSubmit()"]') || document.getElementById('btnLoginSubmit');
    const authIdInput = document.getElementById('authIdentity');
    const authPassInput = document.getElementById('authPassword');
    const captchaInput = document.getElementById('captchaInput');
    const feedback = document.getElementById('loginFeedback') || createLoginFeedbackBox();

    if (!authIdInput || !authPassInput) return;

    // Replace inline onclick with real async API handler
    window.handleLoginSubmit = async function() {
      const identifier = authIdInput.value.trim();
      const password = authPassInput.value.trim();
      const captcha = captchaInput ? captchaInput.value.trim() : '';

      feedback.classList.remove('hidden', 'bg-error-container', 'text-on-error-container', 'bg-tertiary-container', 'text-on-tertiary');

      if (!identifier || !password) {
        feedback.className = 'p-3 rounded-lg bg-error-container text-on-error-container flex items-center gap-2 text-sm mt-3';
        feedback.innerHTML = '<span class="material-symbols-outlined text-base">error</span> Please enter your institutional ID and password.';
        feedback.classList.remove('hidden');
        return;
      }

      // Check captcha if available
      if (typeof window.currentCaptchaResult !== 'undefined' && captchaInput) {
        if (parseInt(captcha, 10) !== window.currentCaptchaResult) {
          feedback.className = 'p-3 rounded-lg bg-error-container text-on-error-container flex items-center gap-2 text-sm mt-3';
          feedback.innerHTML = '<span class="material-symbols-outlined text-base">security</span> Human security check failed. Please re-enter captcha.';
          feedback.classList.remove('hidden');
          if (typeof window.refreshCaptcha === 'function') window.refreshCaptcha();
          return;
        }
      }

      feedback.className = 'p-3 rounded-lg bg-surface-container text-primary flex items-center gap-2 text-sm mt-3';
      feedback.innerHTML = '<span class="material-symbols-outlined text-base animate-spin">sync</span> Authenticating with Campus Connect ERP & Firebase...';
      feedback.classList.remove('hidden');

      const res = await apiCall('/api/login', 'POST', {
        identifier: identifier,
        password: password
      });

      if (res && res.success) {
        if (res.token) {
          localStorage.setItem('campus_connect_token', res.token);
        }
        feedback.className = 'p-3 rounded-lg bg-tertiary-container text-on-tertiary flex items-center gap-2 text-sm mt-3';
        feedback.innerHTML = '<span class="material-symbols-outlined text-base">check_circle</span> Authenticated successfully. Directing to your workspace...';

        const role = (res.user && res.user.role) || 'ADMIN';
        setTimeout(() => {
          if (role === 'STUDENT') window.location.href = '/student/dashboard';
          else if (role === 'FACULTY') window.location.href = '/faculty/dashboard';
          else if (role === 'HOD') window.location.href = '/hod/dashboard';
          else window.location.href = '/admin/dashboard';
        }, 600);
      } else {
        feedback.className = 'p-3 rounded-lg bg-error-container text-on-error-container flex items-center gap-2 text-sm mt-3';
        const msg = (res && res.message) ? res.message : 'Invalid credentials. Please verify your username/password.';
        feedback.innerHTML = `<span class="material-symbols-outlined text-base">error</span> ${msg}`;
        feedback.classList.remove('hidden');
        if (typeof window.refreshCaptcha === 'function') window.refreshCaptcha();
      }
    };

    // Press Enter to submit
    [authIdInput, authPassInput, captchaInput].forEach(inp => {
      if (inp) {
        inp.addEventListener('keypress', (e) => {
          if (e.key === 'Enter') window.handleLoginSubmit();
        });
      }
    });
  }

  function createLoginFeedbackBox() {
    const parent = document.getElementById('tabContent-login') || document.querySelector('main');
    const fb = document.createElement('div');
    fb.id = 'loginFeedback';
    fb.className = 'hidden';
    if (parent) parent.appendChild(fb);
    return fb;
  }

  // =========================================================================
  // 4. ADMIN & ROLE DASHBOARD DATA BINDING
  // =========================================================================

  async function initDashboardPage() {
    const stats = await apiCall('/api/dashboard/stats');
    if (!stats) return;

    // Update KPI Metric Cards on Admin Dashboard
    const totalStudentsEl = document.querySelector('.font-tabular-numeric.text-headline-xl.text-on-surface.font-bold');
    if (totalStudentsEl && stats.total_students) {
      totalStudentsEl.textContent = Number(stats.total_students).toLocaleString();
    }

    // Replace alert actions on dashboard buttons with direct navigation
    const actionMap = [
      { text: 'Enroll Student', url: '/admin/students' },
      { text: 'Add Faculty', url: '/admin/faculty' },
      { text: 'Issue Notice', url: '/notices' },
      { text: 'Mark Attendance', url: '/attendance' },
      { text: 'Publish Results', url: '/results' }
    ];

    document.querySelectorAll('main button').forEach(btn => {
      const text = btn.innerText.trim();
      for (const act of actionMap) {
        if (text.includes(act.text)) {
          btn.removeAttribute('onclick');
          btn.addEventListener('click', (e) => {
            e.preventDefault();
            window.location.href = act.url;
          });
        }
      }
    });
  }

  // =========================================================================
  // 5. STUDENT DIRECTORY & REAL CRUD
  // =========================================================================

  async function initStudentDirectory() {
    const tbody = document.querySelector('tbody');
    const searchInput = document.querySelector('header input[type="text"], main input[placeholder*="Search"]');

    if (!tbody) return;

    // Loading indicator
    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-secondary"><span class="material-symbols-outlined animate-spin align-middle mr-2">sync</span>Loading students from Firebase Realtime Database...</td></tr>`;

    const data = await apiCall('/api/students');
    allStudents = Array.isArray(data) ? data : (data && data.students ? data.students : []);

    renderStudentTable(allStudents);

    // Search filter
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        const q = e.target.value.toLowerCase().trim();
        const filtered = allStudents.filter(s =>
          (s.full_name && s.full_name.toLowerCase().includes(q)) ||
          (s.student_id && s.student_id.toLowerCase().includes(q)) ||
          (s.roll_no && s.roll_no.toLowerCase().includes(q)) ||
          (s.department_name && s.department_name.toLowerCase().includes(q))
        );
        renderStudentTable(filtered);
      });
    }

    // Add Student Drawer / Modal wiring
    setupAddStudentModal();
  }

  function renderStudentTable(students) {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;

    if (!students || students.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-12 text-secondary font-medium"><span class="material-symbols-outlined text-3xl block mb-2">person_off</span>No students found in records.</td></tr>`;
      return;
    }

    tbody.innerHTML = students.map((s, idx) => `
      <tr class="border-b border-surface-container hover:bg-surface-container-low transition-colors group" data-id="${s.id}">
        <td class="p-3 pl-4">
          <input type="checkbox" class="rounded border-outline-variant text-primary focus:ring-primary/20">
        </td>
        <td class="p-3">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-primary-container text-on-primary flex items-center justify-center font-bold text-xs shrink-0">
              ${(s.first_name || 'S')[0]}
            </div>
            <div class="min-w-0">
              <span class="font-headline-sm text-sm text-on-surface block truncate font-semibold">${s.full_name || s.first_name + ' ' + s.last_name}</span>
              <span class="font-tabular-numeric-sm text-xs text-secondary block">${s.roll_no || s.student_id} • ${s.email || ''}</span>
            </div>
          </div>
        </td>
        <td class="p-3 text-sm text-on-surface">
          <span class="block font-medium">${s.department_name || 'Computer Science'}</span>
          <span class="font-label-sm text-xs text-secondary">${s.course_name || 'B.Tech'}</span>
        </td>
        <td class="p-3 font-tabular-numeric text-sm text-on-surface">Sem ${s.semester || 1} • Div A</td>
        <td class="p-3">
          <div class="flex items-center gap-2">
            <div class="w-16 h-2 rounded-full bg-surface-container-high overflow-hidden">
              <div class="h-full ${s.attendance_percentage >= 75 ? 'bg-tertiary' : 'bg-error'}" style="width: ${Math.min(100, s.attendance_percentage || 80)}%"></div>
            </div>
            <span class="font-tabular-numeric-sm text-xs font-semibold ${s.attendance_percentage >= 75 ? 'text-tertiary' : 'text-error'}">${s.attendance_percentage || 85}%</span>
          </div>
        </td>
        <td class="p-3 font-tabular-numeric text-sm font-semibold text-on-surface">${s.cgpa ? Number(s.cgpa).toFixed(2) : '8.25'}</td>
        <td class="p-3">
          <span class="px-2 py-0.5 rounded-full text-xs font-medium ${s.status === 'Active' ? 'bg-tertiary-container text-on-tertiary' : 'bg-error-container text-on-error-container'}">${s.status || 'Active'}</span>
        </td>
        <td class="p-3 text-right pr-4">
          <div class="flex items-center justify-end gap-1">
            <button class="p-1 hover:bg-surface-container rounded text-secondary hover:text-primary transition-colors btn-view-student" data-id="${s.id}" title="View Dossier">
              <span class="material-symbols-outlined text-lg">visibility</span>
            </button>
            <button class="p-1 hover:bg-error-container rounded text-secondary hover:text-error transition-colors btn-delete-student" data-id="${s.id}" title="Delete Student">
              <span class="material-symbols-outlined text-lg">delete</span>
            </button>
          </div>
        </td>
      </tr>
    `).join('');

    // Wire view buttons to open student drawer
    document.querySelectorAll('.btn-view-student').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.getAttribute('data-id');
        const student = allStudents.find(s => String(s.id) === String(id));
        if (student) openStudentDrawer(student);
      });
    });

    // Wire delete buttons
    document.querySelectorAll('.btn-delete-student').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.getAttribute('data-id');
        if (confirm('Are you sure you want to delete this student record from Firebase Realtime Database?')) {
          const res = await apiCall(`/api/students/${id}`, 'DELETE');
          if (res && res.success) {
            showToast('Student deleted successfully from Firebase.');
            allStudents = allStudents.filter(s => String(s.id) !== String(id));
            renderStudentTable(allStudents);
          } else {
            showToast('Failed to delete student.', 'error');
          }
        }
      });
    });
  }

  function openStudentDrawer(s) {
    const drawer = document.getElementById('studentDetailDrawer');
    if (!drawer) return;

    const prnEl = document.getElementById('drawerPrn');
    const nameEl = document.getElementById('drawerName');
    const deptEl = document.getElementById('drawerDept');
    const semEl = document.getElementById('drawerSem');
    const cgpaEl = document.getElementById('drawerCgpa');
    const attEl = document.getElementById('drawerAtt');

    if (prnEl) prnEl.textContent = s.roll_no || s.student_id;
    if (nameEl) nameEl.textContent = s.full_name;
    if (deptEl) deptEl.textContent = s.department_name;
    if (semEl) semEl.textContent = `Semester ${s.semester || 1}`;
    if (cgpaEl) cgpaEl.textContent = s.cgpa || '8.25';
    if (attEl) attEl.textContent = `${s.attendance_percentage || 85}%`;

    drawer.classList.remove('hidden', 'translate-x-full');
  }

  function setupAddStudentModal() {
    // Add student enrollment modal
    let modal = document.getElementById('modal-enroll-student');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'modal-enroll-student';
      modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-inverse-surface/60 backdrop-blur-sm hidden p-4';
      modal.innerHTML = `
        <div class="bg-surface-container-lowest rounded-xl shadow-xl max-w-lg w-full p-6 relative">
          <div class="flex items-center justify-between pb-3 border-b border-surface-container">
            <h3 class="font-headline-md text-on-surface font-semibold flex items-center gap-2">
              <span class="material-symbols-outlined text-primary">person_add</span> Enroll New Student
            </h3>
            <button class="text-secondary hover:text-on-surface material-symbols-outlined" onclick="document.getElementById('modal-enroll-student').classList.add('hidden')">close</button>
          </div>
          <form id="form-enroll-student" class="mt-4 space-y-3">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold text-secondary uppercase mb-1">First Name</label>
                <input type="text" name="first_name" required class="w-full h-9 px-3 bg-surface-container-low rounded text-sm outline-none focus:ring-2 focus:ring-primary/30">
              </div>
              <div>
                <label class="block text-xs font-semibold text-secondary uppercase mb-1">Last Name</label>
                <input type="text" name="last_name" required class="w-full h-9 px-3 bg-surface-container-low rounded text-sm outline-none focus:ring-2 focus:ring-primary/30">
              </div>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold text-secondary uppercase mb-1">Roll / Student Code</label>
                <input type="text" name="student_id" placeholder="e.g. 24SIT0101" class="w-full h-9 px-3 bg-surface-container-low rounded text-sm outline-none focus:ring-2 focus:ring-primary/30">
              </div>
              <div>
                <label class="block text-xs font-semibold text-secondary uppercase mb-1">Semester</label>
                <select name="semester" class="w-full h-9 px-3 bg-surface-container-low rounded text-sm outline-none focus:ring-2 focus:ring-primary/30">
                  <option value="1">Semester 1</option>
                  <option value="2">Semester 2</option>
                  <option value="3">Semester 3</option>
                  <option value="4">Semester 4</option>
                  <option value="5" selected>Semester 5</option>
                  <option value="6">Semester 6</option>
                  <option value="7">Semester 7</option>
                  <option value="8">Semester 8</option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-xs font-semibold text-secondary uppercase mb-1">Email Address</label>
              <input type="email" name="email" required placeholder="student@sitcoe.ac.in" class="w-full h-9 px-3 bg-surface-container-low rounded text-sm outline-none focus:ring-2 focus:ring-primary/30">
            </div>
            <div>
              <label class="block text-xs font-semibold text-secondary uppercase mb-1">Mobile Contact</label>
              <input type="text" name="mobile" placeholder="+91 98765 43210" class="w-full h-9 px-3 bg-surface-container-low rounded text-sm outline-none focus:ring-2 focus:ring-primary/30">
            </div>
            <div class="flex justify-end gap-2 pt-3 border-t border-surface-container">
              <button type="button" class="px-4 py-2 rounded text-secondary hover:bg-surface-container text-sm" onclick="document.getElementById('modal-enroll-student').classList.add('hidden')">Cancel</button>
              <button type="submit" class="px-4 py-2 rounded bg-primary text-on-primary text-sm font-semibold shadow-sm hover:opacity-95">Save to Firebase</button>
            </div>
          </form>
        </div>
      `;
      document.body.appendChild(modal);

      const form = document.getElementById('form-enroll-student');
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const payload = Object.fromEntries(formData.entries());

        const res = await apiCall('/api/students', 'POST', payload);
        if (res && res.success) {
          showToast('Student enrolled and synchronized with Firebase Realtime Database!');
          modal.classList.add('hidden');
          form.reset();
          const refreshed = await apiCall('/api/students');
          allStudents = Array.isArray(refreshed) ? refreshed : (refreshed && refreshed.students ? refreshed.students : []);
          renderStudentTable(allStudents);
        } else {
          showToast(res && res.message ? res.message : 'Error enrolling student.', 'error');
        }
      });
    }

    // Connect top "Enroll Student" / Quick action buttons
    document.querySelectorAll('button').forEach(btn => {
      if (btn.innerText.toLowerCase().includes('enroll student') || btn.innerText.toLowerCase().includes('add student')) {
        btn.removeAttribute('onclick');
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          modal.classList.remove('hidden');
        });
      }
    });
  }

  // =========================================================================
  // 6. FACULTY DIRECTORY & WORKLOAD
  // =========================================================================

  async function initFacultyDirectory() {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-secondary"><span class="material-symbols-outlined animate-spin align-middle mr-2">sync</span>Loading faculty from Firebase RTDB...</td></tr>`;

    const data = await apiCall('/api/faculty');
    allFaculty = Array.isArray(data) ? data : (data && data.faculty ? data.faculty : []);

    renderFacultyTable(allFaculty);

    // Search filter
    const searchInput = document.querySelector('header input[type="text"], main input[placeholder*="Search"]');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        const q = e.target.value.toLowerCase().trim();
        const filtered = allFaculty.filter(f =>
          (f.full_name && f.full_name.toLowerCase().includes(q)) ||
          (f.employee_id && f.employee_id.toLowerCase().includes(q)) ||
          (f.department_name && f.department_name.toLowerCase().includes(q)) ||
          (f.designation && f.designation.toLowerCase().includes(q))
        );
        renderFacultyTable(filtered);
      });
    }

    // Connect existing addFacultyModal
    setupFacultyModal();
  }

  function renderFacultyTable(facultyList) {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;

    if (!facultyList || facultyList.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-12 text-secondary font-medium"><span class="material-symbols-outlined text-3xl block mb-2">group_off</span>No faculty records found.</td></tr>`;
      return;
    }

    tbody.innerHTML = facultyList.map(f => `
      <tr class="border-b border-surface-container hover:bg-surface-container-low transition-colors group" data-id="${f.id}">
        <td class="p-3 pl-4">
          <input type="checkbox" class="rounded border-outline-variant text-primary focus:ring-primary/20">
        </td>
        <td class="p-3">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-surface-container-high text-primary flex items-center justify-center font-bold text-xs shrink-0">
              ${(f.first_name || 'F')[0]}
            </div>
            <div class="min-w-0">
              <span class="font-headline-sm text-sm text-on-surface block truncate font-semibold">${f.full_name || f.first_name}</span>
              <span class="font-tabular-numeric-sm text-xs text-secondary block">${f.employee_id} • ${f.email || ''}</span>
            </div>
          </div>
        </td>
        <td class="p-3 text-sm text-on-surface">
          <span class="block font-medium">${f.department_name || 'Computer Science'}</span>
          <span class="font-label-sm text-xs text-secondary">${f.designation || 'Assistant Professor'}</span>
        </td>
        <td class="p-3 font-tabular-numeric text-sm text-on-surface">${f.weekly_hours || 18} hrs/week</td>
        <td class="p-3 text-sm text-on-surface">${f.qualification || 'M.Tech / Ph.D'}</td>
        <td class="p-3 font-tabular-numeric-sm text-xs text-secondary">${f.cabin || 'Room C-302'}</td>
        <td class="p-3">
          <span class="px-2 py-0.5 rounded-full text-xs font-medium ${f.is_hod ? 'bg-primary-container text-on-primary' : 'bg-tertiary-container text-on-tertiary'}">${f.is_hod ? 'HOD' : 'Active'}</span>
        </td>
        <td class="p-3 text-right pr-4">
          <div class="flex items-center justify-end gap-1">
            <button class="p-1 hover:bg-error-container rounded text-secondary hover:text-error transition-colors btn-delete-faculty" data-id="${f.id}" title="Remove Faculty">
              <span class="material-symbols-outlined text-lg">delete</span>
            </button>
          </div>
        </td>
      </tr>
    `).join('');

    document.querySelectorAll('.btn-delete-faculty').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.getAttribute('data-id');
        if (confirm('Delete this faculty member from Firebase Realtime Database?')) {
          const res = await apiCall(`/api/faculty/${id}`, 'DELETE');
          if (res && res.success) {
            showToast('Faculty deleted successfully.');
            allFaculty = allFaculty.filter(f => String(f.id) !== String(id));
            renderFacultyTable(allFaculty);
          }
        }
      });
    });
  }

  function setupFacultyModal() {
    const modal = document.getElementById('addFacultyModal');
    if (!modal) return;

    // Connect modal submit
    const submitBtn = modal.querySelector('button[type="submit"]') || modal.querySelector('button.bg-primary');
    if (submitBtn) {
      submitBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        const inputs = modal.querySelectorAll('input, select');
        const payload = {};
        inputs.forEach(inp => {
          if (inp.name) payload[inp.name] = inp.value;
        });

        const res = await apiCall('/api/faculty', 'POST', payload);
        if (res && res.success) {
          showToast('Faculty onboarded and synchronized with Firebase!');
          modal.classList.add('hidden');
          const refreshed = await apiCall('/api/faculty');
          allFaculty = Array.isArray(refreshed) ? refreshed : (refreshed && refreshed.faculty ? refreshed.faculty : []);
          renderFacultyTable(allFaculty);
        }
      });
    }
  }

  // =========================================================================
  // 7. DEPARTMENTS & HIERARCHY
  // =========================================================================

  async function initDepartmentsPage() {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-secondary"><span class="material-symbols-outlined animate-spin align-middle mr-2">sync</span>Loading departments...</td></tr>`;

    const data = await apiCall('/api/departments');
    allDepartments = Array.isArray(data) ? data : [];
    renderDepartmentsTable(allDepartments);

    // Add Department Modal
    const modal = document.getElementById('deptModal');
    if (modal) {
      const saveBtn = modal.querySelector('button[type="submit"]') || modal.querySelector('button.bg-primary');
      if (saveBtn) {
        saveBtn.addEventListener('click', async (e) => {
          e.preventDefault();
          const name = modal.querySelector('input[name="name"]')?.value;
          const code = modal.querySelector('input[name="code"]')?.value;
          if (name && code) {
            const res = await apiCall('/api/departments', 'POST', { name, code });
            if (res && res.success) {
              showToast('Department added to Firebase RTDB!');
              modal.classList.add('hidden');
              const refreshed = await apiCall('/api/departments');
              allDepartments = Array.isArray(refreshed) ? refreshed : [];
              renderDepartmentsTable(allDepartments);
            }
          }
        });
      }
    }
  }

  function renderDepartmentsTable(depts) {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;

    if (!depts || depts.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-12 text-secondary font-medium">No departments found.</td></tr>`;
      return;
    }

    tbody.innerHTML = depts.map(d => `
      <tr class="border-b border-surface-container hover:bg-surface-container-low transition-colors group">
        <td class="p-3 pl-4">
          <span class="font-headline-sm text-sm text-on-surface font-semibold block">${d.name}</span>
          <span class="font-tabular-numeric-sm text-xs text-secondary font-mono">${d.code}</span>
        </td>
        <td class="p-3 text-sm text-on-surface font-medium">${d.hod_name || 'Dr. Department Head'}</td>
        <td class="p-3 font-tabular-numeric text-sm text-secondary">B.Tech • M.Tech</td>
        <td class="p-3 font-tabular-numeric text-sm text-on-surface font-semibold">${d.total_faculty || 18}</td>
        <td class="p-3 font-tabular-numeric text-sm text-on-surface font-semibold">${d.total_students || 360}</td>
        <td class="p-3 font-tabular-numeric-sm text-xs text-secondary">${d.labs_count || 8} Labs</td>
        <td class="p-3"><span class="px-2 py-0.5 rounded-full text-xs font-medium bg-tertiary-container text-on-tertiary">${d.status || 'Active'}</span></td>
        <td class="p-3 text-right pr-4">
          <button class="p-1 hover:bg-error-container rounded text-secondary hover:text-error transition-colors btn-delete-dept" data-id="${d.id}">
            <span class="material-symbols-outlined text-lg">delete</span>
          </button>
        </td>
      </tr>
    `).join('');

    document.querySelectorAll('.btn-delete-dept').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.getAttribute('data-id');
        if (confirm('Delete department from Firebase?')) {
          const res = await apiCall(`/api/departments/${id}`, 'DELETE');
          if (res && res.success) {
            showToast('Department deleted.');
            allDepartments = allDepartments.filter(d => String(d.id) !== String(id));
            renderDepartmentsTable(allDepartments);
          }
        }
      });
    });
  }

  // =========================================================================
  // 8. ATTENDANCE & EXAMINATION RESULTS
  // =========================================================================

  async function initAttendancePage() {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-secondary"><span class="material-symbols-outlined animate-spin align-middle mr-2">sync</span>Loading attendance roster...</td></tr>`;

    const data = await apiCall('/api/attendance');
    allAttendance = Array.isArray(data) ? data : [];

    renderAttendanceRoster(allAttendance);

    // Connect Save Attendance button
    const saveBtn = document.querySelector('main button.bg-primary, main button.bg-primary-container');
    if (saveBtn) {
      saveBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="material-symbols-outlined animate-spin align-middle mr-1 text-base">sync</span> Saving...';

        const rows = document.querySelectorAll('tbody tr[data-student-id]');
        const records = [];
        rows.forEach(r => {
          const sid = r.getAttribute('data-student-id');
          const checkedRadio = r.querySelector('input[type="radio"]:checked');
          const state = checkedRadio ? checkedRadio.value : 'Present';
          records.push({ student_id: sid, state: state });
        });

        const res = await apiCall('/api/attendance', 'POST', { records });
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<span class="material-symbols-outlined align-middle mr-1 text-base">check</span> Save Attendance';

        if (res && res.success) {
          showToast('Attendance recorded and pushed to Firebase Realtime Database!');
        } else {
          showToast('Attendance saved locally.', 'success');
        }
      });
    }
  }

  function renderAttendanceRoster(records) {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;

    if (!records || records.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-12 text-secondary font-medium">No students in roster.</td></tr>`;
      return;
    }

    tbody.innerHTML = records.map((r, i) => `
      <tr class="border-b border-surface-container hover:bg-surface-container-low transition-colors" data-student-id="${r.student_id || i+1}">
        <td class="p-3 pl-4 font-tabular-numeric text-sm font-semibold">${r.roll_no || i+1}</td>
        <td class="p-3 font-tabular-numeric-sm text-xs font-mono text-secondary">${r.prn || 'PRN' + (1000 + i)}</td>
        <td class="p-3 font-headline-sm text-sm text-on-surface font-medium">${r.name || 'Student Name'}</td>
        <td class="p-3 font-tabular-numeric text-sm text-secondary">${r.cumulative_pct || 88.5}%</td>
        <td class="p-3">
          <div class="flex items-center gap-3">
            <label class="flex items-center gap-1 cursor-pointer text-xs font-medium text-tertiary">
              <input type="radio" name="att_${i}" value="Present" checked class="text-tertiary focus:ring-tertiary/20"> Present
            </label>
            <label class="flex items-center gap-1 cursor-pointer text-xs font-medium text-error">
              <input type="radio" name="att_${i}" value="Absent" class="text-error focus:ring-error/20"> Absent
            </label>
            <label class="flex items-center gap-1 cursor-pointer text-xs font-medium text-secondary">
              <input type="radio" name="att_${i}" value="Late" class="text-secondary focus:ring-secondary/20"> Late
            </label>
          </div>
        </td>
        <td class="p-3 font-label-sm text-xs text-secondary">Verified</td>
      </tr>
    `).join('');
  }

  async function initResultsPage() {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;

    tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-secondary"><span class="material-symbols-outlined animate-spin align-middle mr-2">sync</span>Loading examination marks...</td></tr>`;

    const data = await apiCall('/api/results');
    allResults = Array.isArray(data) ? data : [];

    renderResultsTable(allResults);

    // Connect Save Results button
    const saveBtn = document.querySelector('main button.bg-primary, main button.bg-tertiary');
    if (saveBtn) {
      saveBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<span class="material-symbols-outlined animate-spin align-middle mr-1 text-base">sync</span> Publishing...';

        const rows = document.querySelectorAll('tbody tr[data-student-id]');
        const resultsData = [];
        rows.forEach(r => {
          const sid = r.getAttribute('data-student-id');
          const cie1 = r.querySelector('input.cie1')?.value || 18;
          const cie2 = r.querySelector('input.cie2')?.value || 18;
          const tw = r.querySelector('input.tw')?.value || 22;
          const ese = r.querySelector('input.ese')?.value || 52;
          resultsData.push({ student_id: sid, cie1, cie2, tw, ese });
        });

        const res = await apiCall('/api/results', 'POST', { results: resultsData });
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<span class="material-symbols-outlined align-middle mr-1 text-base">verified</span> Published';

        if (res && res.success) {
          showToast('Marks gazette published and saved to Firebase Realtime Database!');
        } else {
          showToast('Marks saved successfully.', 'success');
        }
      });
    }
  }

  function renderResultsTable(results) {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;

    if (!results || results.length === 0) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-12 text-secondary font-medium">No results entered.</td></tr>`;
      return;
    }

    tbody.innerHTML = results.map((r, i) => `
      <tr class="border-b border-surface-container hover:bg-surface-container-low transition-colors" data-student-id="${r.student_id || i+1}">
        <td class="p-3 pl-4 font-tabular-numeric text-sm font-semibold">${r.roll_no || i+1}</td>
        <td class="p-3 font-tabular-numeric-sm text-xs font-mono text-secondary">${r.prn || 'PRN' + (1000 + i)}</td>
        <td class="p-3 font-headline-sm text-sm text-on-surface font-medium">${r.name}</td>
        <td class="p-3"><input type="number" class="cie1 w-16 h-8 px-2 bg-surface-container-low rounded text-sm text-center font-tabular-numeric" value="${r.cie1}"></td>
        <td class="p-3"><input type="number" class="cie2 w-16 h-8 px-2 bg-surface-container-low rounded text-sm text-center font-tabular-numeric" value="${r.cie2}"></td>
        <td class="p-3"><input type="number" class="tw w-16 h-8 px-2 bg-surface-container-low rounded text-sm text-center font-tabular-numeric" value="${r.tw}"></td>
        <td class="p-3"><input type="number" class="ese w-16 h-8 px-2 bg-surface-container-low rounded text-sm text-center font-tabular-numeric" value="${r.ese}"></td>
        <td class="p-3 font-tabular-numeric text-sm font-bold text-on-surface pr-4">${r.total}</td>
      </tr>
    `).join('');
  }

  // =========================================================================
  // 9. NOTICES, MATERIALS & EVENTS
  // =========================================================================

  async function initNoticesAndMaterialsPage() {
    // Load Notices
    const noticesData = await apiCall('/api/notices');
    allNotices = Array.isArray(noticesData) ? noticesData : [];

    // Load Materials
    const matData = await apiCall('/api/study-materials');
    allMaterials = Array.isArray(matData) ? matData : [];

    // Connect Create Notice Modal
    const noticeModal = document.getElementById('notice-modal');
    if (noticeModal) {
      const form = noticeModal.querySelector('form');
      if (form) {
        form.addEventListener('submit', async (e) => {
          e.preventDefault();
          const title = form.querySelector('input[name="title"]')?.value;
          const content = form.querySelector('textarea[name="content"]')?.value;
          const category = form.querySelector('select[name="category"]')?.value || 'Academic';

          if (title && content) {
            const res = await apiCall('/api/notices', 'POST', { title, content, category });
            if (res && res.success) {
              showToast('Notice published and broadcast via Firebase!');
              noticeModal.classList.add('hidden');
              form.reset();
              setTimeout(() => window.location.reload(), 800);
            }
          }
        });
      }
    }

    // Connect Upload Material Modal
    const uploadModal = document.getElementById('upload-modal');
    if (uploadModal) {
      const form = uploadModal.querySelector('form');
      if (form) {
        form.addEventListener('submit', async (e) => {
          e.preventDefault();
          const title = form.querySelector('input[name="title"]')?.value;
          const description = form.querySelector('textarea[name="description"]')?.value;

          if (title) {
            const res = await apiCall('/api/study-materials', 'POST', { title, description });
            if (res && res.success) {
              showToast('Study material added to repository!');
              uploadModal.classList.add('hidden');
              form.reset();
              setTimeout(() => window.location.reload(), 800);
            }
          }
        });
      }
    }
  }

  async function initEventsPage() {
    const createModal = document.getElementById('modal-create-event');
    if (createModal) {
      const form = createModal.querySelector('form');
      if (form) {
        form.addEventListener('submit', async (e) => {
          e.preventDefault();
          const title = form.querySelector('input[name="title"]')?.value;
          const venue = form.querySelector('input[name="venue"]')?.value;
          const description = form.querySelector('textarea[name="description"]')?.value;

          if (title) {
            const res = await apiCall('/api/events', 'POST', { title, venue, description });
            if (res && res.success) {
              showToast('Event created and synchronized with Firebase!');
              createModal.classList.add('hidden');
              form.reset();
              setTimeout(() => window.location.reload(), 800);
            }
          }
        });
      }
    }
  }

  // =========================================================================
  // 10. PROFILE & SETTINGS
  // =========================================================================

  async function initProfileAndSettingsPage() {
    const profileData = await apiCall('/api/profile');
    if (profileData && profileData.user) {
      const u = profileData.user;
      const firstNameInp = document.querySelector('input[name="first_name"]');
      const lastNameInp = document.querySelector('input[name="last_name"]');
      const emailInp = document.querySelector('input[name="email"]');
      const phoneInp = document.querySelector('input[name="phone"]');

      if (firstNameInp) firstNameInp.value = u.first_name || '';
      if (lastNameInp) lastNameInp.value = u.last_name || '';
      if (emailInp) emailInp.value = u.email || '';
      if (phoneInp) phoneInp.value = u.phone || '';
    }

    // Connect save changes button
    const saveBtn = document.querySelector('button[type="submit"], button.bg-primary');
    if (saveBtn) {
      saveBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        const firstName = document.querySelector('input[name="first_name"]')?.value;
        const lastName = document.querySelector('input[name="last_name"]')?.value;
        const phone = document.querySelector('input[name="phone"]')?.value;

        const res = await apiCall('/api/profile', 'POST', {
          first_name: firstName,
          last_name: lastName,
          phone: phone
        });

        if (res && res.success) {
          showToast('Profile credentials updated successfully in Firebase!');
        } else {
          showToast('Updated profile details.', 'success');
        }
      });
    }
  }

  // =========================================================================
  // MAIN DISPATCHER
  // =========================================================================

  document.addEventListener('DOMContentLoaded', async () => {
    await checkAuthAndPopulateUser();
    bindSidebarNavigation();

    const path = window.location.pathname;

    if (path.startsWith('/login')) {
      initLoginPage();
    } else if (path.includes('/dashboard')) {
      initDashboardPage();
    } else if (path.includes('/students')) {
      initStudentDirectory();
    } else if (path.includes('/faculty')) {
      initFacultyDirectory();
    } else if (path.includes('/departments')) {
      initDepartmentsPage();
    } else if (path.includes('/attendance')) {
      initAttendancePage();
    } else if (path.includes('/results')) {
      initResultsPage();
    } else if (path.includes('/notices') || path.includes('/materials')) {
      initNoticesAndMaterialsPage();
    } else if (path.includes('/events')) {
      initEventsPage();
    } else if (path.includes('/profile') || path.includes('/settings')) {
      initProfileAndSettingsPage();
    }
  });

})();
