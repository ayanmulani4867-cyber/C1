/**
 * Campus Connect ERP - Multi-Tab Isolated Web Authentication & SPA Navigation Engine
 * Manages per-tab sessionStorage Bearer token lifecycle, authenticated fetch requests,
 * and DOM updates without document.write or shared cookie dependencies.
 */
(function() {
    'use strict';

    const TOKEN_KEY = 'CAMPUS_CONNECT_ERP_token';

    function getToken() {
        try {
            return sessionStorage.getItem(TOKEN_KEY);
        } catch (e) {
            return null;
        }
    }

    function setToken(token) {
        try {
            sessionStorage.setItem(TOKEN_KEY, token);
        } catch (e) {}
    }

    function clearToken() {
        try {
            sessionStorage.removeItem(TOKEN_KEY);
        } catch (e) {}
    }

    /**
     * Parse and render full Jinja HTML document into the browser DOM
     */
    window.__erp_renderPage = function(html, targetUrl) {
        if (!html) return;

        const parser = new DOMParser();
        const newDoc = parser.parseFromString(html, 'text/html');

        // 1. Synchronize Document Title & <html> attributes
        if (newDoc.title) {
            document.title = newDoc.title;
        }
        if (newDoc.documentElement.lang) {
            document.documentElement.lang = newDoc.documentElement.lang;
        }

        // 2. Synchronize Head Stylesheets & Inline Styles
        // Remove any prior inline <style> elements (including bootstrap-specific styles)
        document.head.querySelectorAll('style').forEach(s => s.remove());
        const erpBootstrapStyle = document.getElementById('erp-bootstrap-style');
        if (erpBootstrapStyle) erpBootstrapStyle.remove();

        // Insert all <style> tags from the new document
        newDoc.head.querySelectorAll('style').forEach(st => {
            const newStyle = document.createElement('style');
            newStyle.textContent = st.textContent;
            document.head.appendChild(newStyle);
        });

        // Synchronize Stylesheets (<link rel="stylesheet">)
        const currentLinks = new Set(Array.from(document.head.querySelectorAll('link[rel="stylesheet"]')).map(l => l.href));
        newDoc.head.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
            if (!currentLinks.has(link.href)) {
                const newLink = document.createElement('link');
                Array.from(link.attributes).forEach(attr => newLink.setAttribute(attr.name, attr.value));
                document.head.appendChild(newLink);
            }
        });

        // 3. Update Body Attributes and Inner HTML
        document.body.className = newDoc.body.className || '';
        if (newDoc.body.getAttribute('style')) {
            document.body.style.cssText = newDoc.body.style.cssText;
        } else {
            document.body.removeAttribute('style');
        }
        document.body.innerHTML = newDoc.body.innerHTML;

        // 4. Re-execute Scripts in DOM Order (excluding this manager script itself)
        const scripts = Array.from(newDoc.querySelectorAll('script'));
        scripts.forEach(oldScript => {
            if (oldScript.src && oldScript.src.includes('erp_multitab_auth.js')) return;
            if (oldScript.id === 'erp-multitab-auth-script' || oldScript.id === 'erp-bootstrap-script') return;

            const newScript = document.createElement('script');
            Array.from(oldScript.attributes).forEach(attr => {
                newScript.setAttribute(attr.name, attr.value);
            });
            if (oldScript.textContent) {
                newScript.textContent = oldScript.textContent;
            }
            document.body.appendChild(newScript);
        });

        // 5. Scroll to top
        window.scrollTo(0, 0);

        // 6. Initialize Bootstrap components if available
        if (window.bootstrap) {
            try {
                document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => new window.bootstrap.Tooltip(el));
                document.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => new window.bootstrap.Popover(el));
            } catch (e) {}
        }
    };

    /**
     * Authenticated Navigation Engine
     */
    window.__erp_navigate = function(path, pushState = true) {
        const token = getToken();
        const headers = {
            'X-ERP-Client': 'web'
        };
        if (token) {
            headers['Authorization'] = 'Bearer ' + token;
        }

        fetch(path, {
            method: 'GET',
            headers: headers
        })
        .then(res => {
            if (res.status === 401 || res.status === 403) {
                clearToken();
                const nextParam = encodeURIComponent(path);
                window.__erp_navigate('/auth/login?next=' + nextParam);
                return null;
            }
            const finalUrl = res.url || path;
            const targetUrlObj = new URL(finalUrl, window.location.origin);
            const targetRelative = targetUrlObj.pathname + targetUrlObj.search + targetUrlObj.hash;

            if (pushState) {
                window.history.pushState({ path: targetRelative }, '', targetRelative);
            } else {
                window.history.replaceState({ path: targetRelative }, '', targetRelative);
            }
            return res.text();
        })
        .then(html => {
            if (html) {
                window.__erp_renderPage(html, path);
            }
        })
        .catch(err => {
            console.error('ERP Navigation error:', err);
        });
    };

    // Global Click Interceptor for Links
    document.addEventListener('click', function(e) {
        const link = e.target.closest('a');
        if (!link) return;

        const href = link.getAttribute('href');
        if (!href || href.startsWith('#') || href.startsWith('javascript:') || href.startsWith('mailto:') || href.startsWith('tel:')) {
            return;
        }
        if (link.target === '_blank' || link.hasAttribute('download')) {
            return;
        }

        const url = new URL(link.href, window.location.origin);
        if (url.origin !== window.location.origin) {
            return;
        }

        // Handle Logout specially
        if (url.pathname === '/auth/logout' || url.pathname.endsWith('/logout')) {
            e.preventDefault();
            clearToken();
            window.__erp_navigate('/auth/login');
            return;
        }

        e.preventDefault();
        const targetPath = url.pathname + url.search + url.hash;
        window.__erp_navigate(targetPath);
    });

    // Global Form Submission Interceptor
    document.addEventListener('submit', function(e) {
        const form = e.target;
        if (!form || form.tagName !== 'FORM') return;

        const action = form.getAttribute('action') || window.location.pathname;
        const method = (form.getAttribute('method') || 'GET').toUpperCase();
        const actionUrl = new URL(action, window.location.origin);

        if (actionUrl.origin !== window.location.origin) {
            return;
        }

        // 1. Intercept Login Form Submission
        if (actionUrl.pathname === '/auth/login' && method === 'POST') {
            e.preventDefault();
            const formData = new FormData(form);
            const identifier = formData.get('identifier') || formData.get('username') || formData.get('email') || '';
            const password = formData.get('password') || '';
            const rememberMe = formData.get('remember_me') === 'y' || formData.get('remember_me') === 'true' || formData.get('remember_me') === 'on';

            fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    identifier: typeof identifier === 'string' ? identifier.trim() : identifier,
                    password: password,
                    remember_me: rememberMe
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success && data.token) {
                    setToken(data.token);

                    const urlParams = new URLSearchParams(window.location.search);
                    let nextUrl = urlParams.get('next');
                    if (!nextUrl || nextUrl.startsWith('/auth/login') || nextUrl.startsWith('/auth/logout')) {
                        const role = (data.user && data.user.role) ? String(data.user.role).toUpperCase() : '';
                        if (role === 'ADMIN') {
                            nextUrl = '/admin/dashboard';
                        } else if (role === 'STUDENT') {
                            nextUrl = '/student/dashboard';
                        } else {
                            nextUrl = '/faculty/dashboard';
                        }
                    }
                    window.__erp_navigate(nextUrl);
                } else {
                    const errorMsg = data.message || 'Invalid username/email or password. Please check your credentials.';
                    let alertDiv = form.parentElement.querySelector('.alert-danger');
                    if (!alertDiv) {
                        alertDiv = document.createElement('div');
                        alertDiv.className = 'alert alert-danger alert-dismissible fade show d-flex align-items-center gap-2 shadow-sm rounded-3 mb-3';
                        alertDiv.innerHTML = '<i class="fa-solid fa-circle-exclamation"></i><div class="small erp-error-text"></div><button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
                        form.parentElement.insertBefore(alertDiv, form);
                    }
                    const textNode = alertDiv.querySelector('.erp-error-text') || alertDiv;
                    textNode.textContent = errorMsg;
                }
            })
            .catch(err => {
                console.error('Login submit error:', err);
            });
            return;
        }

        // 2. Intercept All Other Forms (POST / GET)
        e.preventDefault();
        const token = getToken();
        const headers = {
            'X-ERP-Client': 'web'
        };
        if (token) {
            headers['Authorization'] = 'Bearer ' + token;
        }

        let fetchOptions = {
            method: method,
            headers: headers
        };

        if (method === 'POST') {
            fetchOptions.body = new FormData(form);
        } else {
            const formData = new FormData(form);
            const params = new URLSearchParams(formData);
            actionUrl.search = params.toString();
        }

        fetch(actionUrl.toString(), fetchOptions)
        .then(res => {
            if (res.status === 401 || res.status === 403) {
                clearToken();
                window.__erp_navigate('/auth/login?next=' + encodeURIComponent(window.location.pathname));
                return null;
            }
            const finalUrl = res.url || actionUrl.toString();
            const targetUrlObj = new URL(finalUrl, window.location.origin);
            const targetRelative = targetUrlObj.pathname + targetUrlObj.search + targetUrlObj.hash;

            window.history.pushState({ path: targetRelative }, '', targetRelative);
            return res.text();
        })
        .then(html => {
            if (html) {
                window.__erp_renderPage(html, window.location.href);
            }
        })
        .catch(err => {
            console.error('Form submission error:', err);
        });
    });

    // History Popstate Interceptor (Back / Forward navigation)
    window.addEventListener('popstate', function() {
        window.__erp_navigate(window.location.pathname + window.location.search + window.location.hash, false);
    });

    // On Initial Execution: check if user is already logged in on /auth/login or /
    const token = getToken();
    const pathname = window.location.pathname;
    if ((pathname === '/auth/login' || pathname === '/') && token) {
        fetch('/api/auth/me', {
            headers: {
                'Authorization': 'Bearer ' + token,
                'X-ERP-Client': 'web'
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success && data.user) {
                const role = String(data.user.role).toUpperCase();
                let dash = '/faculty/dashboard';
                if (role === 'ADMIN') dash = '/admin/dashboard';
                else if (role === 'STUDENT') dash = '/student/dashboard';
                window.__erp_navigate(dash);
            } else {
                clearToken();
            }
        })
        .catch(() => {
            clearToken();
        });
    }
})();
