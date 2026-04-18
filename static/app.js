/**
 * Job Tracker — Frontend
 */

// ─── SVG Icons ───────────────────────────────────────────────────────────────
const IC = {
    scan:    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 16h5v5"/></svg>`,
    sparkle: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/></svg>`,
    archive: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="5" x="2" y="3" rx="1"/><path d="M4 8v11a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8"/><path d="M10 12h4"/></svg>`,
    restore: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7v6h6"/><path d="M21 17a9 9 0 0 0-15-6.7L3 13"/></svg>`,
    trash:   `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>`,
    more:    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="5" cy="12" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="19" cy="12" r="1.5"/></svg>`,
    sun:     `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>`,
    moon:    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>`,
    search:  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>`,
    logout:  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>`,
    close:   `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18M6 6l12 12"/></svg>`,
    mail:    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>`,
    inbox:   `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></svg>`,
    checkOk: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>`,
    warn:    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>`,
    info:    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>`,
    google:  `<svg viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>`,
};

// ─── State ────────────────────────────────────────────────────────────────────
const state = {
    authenticated: false,
    emails: [],
    stats: { total: 0, categories: {}, recent_7_days: 0 },
    currentCategory: 'all',
    searchQuery: '',
    currentPage: 1,
    totalPages: 1,
    totalEmails: 0,
    isScanning: false,
    isReclassifying: false,
    isLoading: true,
    theme: localStorage.getItem('theme') || 'dark',
};

// ─── Category Config ──────────────────────────────────────────────────────────
const CATEGORIES = {
    all:       { label: 'All' },
    rejection: { label: 'Rejected' },
    interview: { label: 'Interview' },
    offer:     { label: 'Offer' },
    follow_up: { label: 'Follow-up' },
    applied:   { label: 'Applied' },
    direct:    { label: 'Direct' },
    other:     { label: 'Other' },
    archived:  { label: 'Archived' },
};

// ─── API ──────────────────────────────────────────────────────────────────────
async function api(path, options = {}) {
    try {
        const res = await fetch(path, {
            headers: { 'Content-Type': 'application/json' },
            ...options,
        });
        return await res.json();
    } catch (err) {
        console.error(`API error (${path}):`, err);
        showToast('Network error. Please try again.', 'error');
        return null;
    }
}

// ─── Init ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', init);

async function init() {
    applyTheme(state.theme);
    const authRes = await api('/api/auth/status');
    state.authenticated = authRes?.authenticated || false;
    if (state.authenticated) {
        await loadDashboard();
    } else {
        renderAuthScreen();
    }
}

async function loadDashboard() {
    state.isLoading = true;
    renderDashboard();
    await Promise.all([loadStats(), loadEmails()]);
    state.isLoading = false;
    renderDashboard();
}

async function loadStats() {
    const data = await api('/api/stats');
    if (data) state.stats = data;
}

async function loadEmails() {
    const params = new URLSearchParams({
        category: state.currentCategory,
        search: state.searchQuery,
        page: state.currentPage,
        per_page: 50,
    });
    const data = await api(`/api/emails?${params}`);
    if (data) {
        state.emails = data.emails;
        state.totalPages = data.total_pages;
        state.totalEmails = data.total;
        state.currentPage = data.page;
    }
}

// ─── Actions ──────────────────────────────────────────────────────────────────
async function scanEmails() {
    if (state.isScanning || state.isReclassifying) return;
    state.isScanning = true;
    renderHeaderActions();
    showToast('Scanning Gmail for job emails…', 'info');

    const result = await api('/api/scan', { method: 'POST', body: JSON.stringify({}) });
    state.isScanning = false;

    if (result?.success) {
        showToast(result.message, 'success');
        await loadDashboard();
    } else {
        showToast(result?.error || 'Scan failed.', 'error');
        renderHeaderActions();
    }
}

async function archiveEmail(emailId, event) {
    if (event) event.stopPropagation();
    const result = await api(`/api/emails/${emailId}/archive`, { method: 'POST' });
    if (result?.success) {
        showToast('Archived', 'success');
        await Promise.all([loadStats(), loadEmails()]);
        renderEmailList();
        renderCategoryTabs();
        renderPagination();
    }
}

async function unarchiveEmail(emailId, event) {
    if (event) event.stopPropagation();
    const result = await api(`/api/emails/${emailId}/unarchive`, { method: 'POST' });
    if (result?.success) {
        showToast('Restored to active', 'success');
        await Promise.all([loadStats(), loadEmails()]);
        renderEmailList();
        renderCategoryTabs();
        renderPagination();
    }
}

async function bulkArchiveRejections() {
    const count = state.stats.categories?.rejection || 0;
    if (count === 0) {
        showToast('No active rejections to archive.', 'info');
        return;
    }
    if (!confirm(`Archive all ${count} rejection emails? They'll be moved to the Archived tab and hidden from the main view.`)) return;

    const result = await api('/api/archive/bulk', {
        method: 'POST',
        body: JSON.stringify({ category: 'rejection' }),
    });
    if (result?.success) {
        showToast(result.message, 'success');
        await loadDashboard();
    }
}

async function cleanupOld() {
    const months = prompt(
        'Delete emails older than how many months?\n\n' +
        'This permanently removes only "other" (noise) emails older than the threshold. ' +
        'Rejections, interviews, offers, etc. are kept.\n\n' +
        'Enter number of months (e.g. 6):',
        '6'
    );
    if (!months) return;
    const days = Math.round(parseFloat(months) * 30);
    if (!days || days < 1) {
        showToast('Invalid number of months.', 'error');
        return;
    }

    const result = await api('/api/cleanup', {
        method: 'POST',
        body: JSON.stringify({ days, categories: ['other'] }),
    });
    if (result?.success) {
        showToast(result.message, 'success');
        await loadDashboard();
    }
}

async function reclassifyEmails() {
    if (state.isScanning || state.isReclassifying) return;
    state.isReclassifying = true;
    renderHeaderActions();
    showToast('Re-classifying all stored emails…', 'info');

    const result = await api('/api/reclassify', { method: 'POST', body: JSON.stringify({}) });
    state.isReclassifying = false;

    if (result?.success) {
        const msg = result.changed > 0
            ? `${result.changed} of ${result.total} emails were re-categorized.`
            : `All ${result.total} emails are already correctly categorized.`;
        showToast(msg, 'success');
        await loadDashboard();
    } else {
        showToast(result?.error || 'Reclassify failed.', 'error');
        renderHeaderActions();
    }
}

function setCategory(category) {
    state.currentCategory = category;
    state.currentPage = 1;
    refreshEmails();
}

let searchTimeout;
function onSearch(query) {
    state.searchQuery = query;
    state.currentPage = 1;
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(refreshEmails, 300);
}

function setPage(page) {
    state.currentPage = page;
    refreshEmails();
}

async function refreshEmails() {
    await loadEmails();
    renderEmailList();
    renderPagination();
    renderCategoryTabs();
}

async function handleLogout() {
    await api('/api/auth/logout', { method: 'POST' });
    state.authenticated = false;
    renderAuthScreen();
}

function toggleTheme() {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('theme', state.theme);
    applyTheme(state.theme);
    renderHeaderActions();
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
}

// ─── Rendering ────────────────────────────────────────────────────────────────
function renderAuthScreen() {
    document.getElementById('headerActions').innerHTML = '';
    document.getElementById('mainContent').innerHTML = `
        <div class="auth-screen">
            <div class="auth-card">
                <div class="auth-icon">${IC.mail}</div>
                <h2>Connect Gmail</h2>
                <p>Link your Gmail account to automatically find and categorize all your job application emails — rejections, interviews, offers, and more.</p>
                <a href="/api/auth" class="btn btn-google">
                    ${IC.google}
                    Sign in with Google
                </a>
            </div>
        </div>
    `;
}

function renderDashboard() {
    renderHeaderActions();
    document.getElementById('mainContent').innerHTML = `
        <div class="stats-grid" id="statsGrid"></div>
        <div class="toolbar">
            <div class="search-wrapper">
                <span class="search-icon">${IC.search}</span>
                <input
                    type="text"
                    class="search-input"
                    id="searchInput"
                    placeholder="Search company, subject, or keyword…"
                    value="${escapeHtml(state.searchQuery)}"
                    oninput="onSearch(this.value)"
                >
            </div>
            <div class="category-tabs" id="categoryTabs"></div>
        </div>
        <div class="email-list" id="emailList"></div>
        <div class="pagination" id="pagination"></div>
    `;

    renderStats();
    renderCategoryTabs();

    if (state.isLoading) {
        renderSkeletons();
    } else {
        renderEmailList();
        renderPagination();
    }
}

function renderHeaderActions() {
    const busy = state.isScanning || state.isReclassifying;
    document.getElementById('headerActions').innerHTML = `
        <div class="menu-wrapper">
            <button class="icon-btn" onclick="toggleMenu(event)" title="More actions">
                ${IC.more}
            </button>
            <div class="menu" id="headerMenu" hidden>
                <button class="menu-item" onclick="closeMenu(); bulkArchiveRejections()">
                    ${IC.archive}
                    <span>Archive all rejections</span>
                </button>
                <button class="menu-item" onclick="closeMenu(); cleanupOld()">
                    ${IC.trash}
                    <span>Clean up old noise…</span>
                </button>
                <button class="menu-item" onclick="closeMenu(); restoreArchived()">
                    ${IC.restore}
                    <span>Restore all archived</span>
                </button>
                <div class="menu-divider"></div>
                <button class="menu-item" onclick="closeMenu(); reclassifyEmails()" ${busy ? 'disabled' : ''}>
                    ${IC.sparkle}
                    <span>Re-classify stored emails</span>
                </button>
            </div>
        </div>
        <button class="icon-btn" onclick="toggleTheme()" title="Toggle theme">
            ${state.theme === 'dark' ? IC.sun : IC.moon}
        </button>
        <button class="btn btn-primary ${state.isScanning ? 'loading' : ''}" onclick="scanEmails()" ${busy ? 'disabled' : ''}>
            <span class="spinner"></span>
            ${state.isScanning ? '' : IC.scan}
            <span class="btn-label">${state.isScanning ? 'Scanning…' : 'Scan'}</span>
        </button>
        <button class="btn btn-ghost" onclick="handleLogout()" title="Sign out">
            ${IC.logout}
            <span class="btn-label">Sign out</span>
        </button>
    `;
}

function toggleMenu(event) {
    event.stopPropagation();
    const m = document.getElementById('headerMenu');
    if (!m) return;
    const opening = m.hasAttribute('hidden');
    m.toggleAttribute('hidden');
    if (opening) {
        setTimeout(() => document.addEventListener('click', closeMenu, { once: true }), 0);
    }
}

function closeMenu() {
    const m = document.getElementById('headerMenu');
    if (m) m.setAttribute('hidden', '');
}

async function restoreArchived() {
    const archived = state.stats.archived || 0;
    if (archived === 0) {
        showToast('No archived emails to restore.', 'info');
        return;
    }
    if (!confirm(`Restore all ${archived} archived emails to the active view?`)) return;
    const result = await api('/api/archive/restore', { method: 'POST' });
    if (result?.success) {
        showToast(result.message, 'success');
        await loadDashboard();
    }
}

function renderStats() {
    const grid = document.getElementById('statsGrid');
    if (!grid) return;

    const cats = state.stats.categories || {};
    const items = [
        { key: 'total',     label: 'Total',      value: state.stats.total || 0 },
        { key: 'rejection', label: 'Rejected',    value: cats.rejection || 0 },
        { key: 'interview', label: 'Interviews',  value: cats.interview || 0 },
        { key: 'offer',     label: 'Offers',      value: cats.offer || 0 },
        { key: 'follow_up', label: 'Follow-ups',  value: cats.follow_up || 0 },
        { key: 'applied',   label: 'Applied',     value: cats.applied || 0 },
        { key: 'direct',    label: 'Direct',      value: cats.direct || 0 },
    ];

    grid.innerHTML = items.map(s => `
        <div class="stat-card ${s.key}">
            <div class="stat-value">${s.value}</div>
            <div class="stat-label">${s.label}</div>
        </div>
    `).join('');
}

function renderCategoryTabs() {
    const tabs = document.getElementById('categoryTabs');
    if (!tabs) return;

    const cats = state.stats.categories || {};
    const total = state.stats.total || 0;

    tabs.innerHTML = Object.entries(CATEGORIES).map(([key, conf]) => {
        let count;
        if (key === 'all')           count = total;
        else if (key === 'archived') count = state.stats.archived || 0;
        else                         count = cats[key] || 0;

        if (key === 'archived' && count === 0) return '';

        const active = state.currentCategory === key ? 'active' : '';
        return `
            <button class="tab-btn ${active}" onclick="setCategory('${key}')">
                ${conf.label}
                <span class="tab-count">${count}</span>
            </button>
        `;
    }).join('');
}

function renderEmailList() {
    const list = document.getElementById('emailList');
    if (!list) return;

    if (state.emails.length === 0) {
        list.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">${state.searchQuery ? IC.search : IC.inbox}</div>
                <h3>${state.searchQuery ? 'No matching emails' : 'No emails yet'}</h3>
                <p>${state.searchQuery
                    ? 'Try a different search term or clear your filters.'
                    : 'Click Scan to fetch and classify your job application emails from Gmail.'
                }</p>
            </div>
        `;
        return;
    }

    list.innerHTML = state.emails.map(email => {
        const cat = CATEGORIES[email.category] || CATEGORIES.other;
        const date = formatDate(email.date);
        const company = email.company_name
            ? `<span class="email-company">${escapeHtml(email.company_name)}</span>` : '';
        const jobTitle = email.job_title
            ? `<span class="email-job-title">${escapeHtml(email.job_title)}</span>` : '';
        const sep = company && jobTitle
            ? '<span class="email-divider">·</span>' : '';

        const isArchived = !!email.is_archived;
        const action = isArchived
            ? `<button class="card-action" onclick='unarchiveEmail(${JSON.stringify(email.id)}, event)' title="Restore to active">${IC.restore}</button>`
            : `<button class="card-action" onclick='archiveEmail(${JSON.stringify(email.id)}, event)' title="Archive">${IC.archive}</button>`;

        return `
            <div class="email-card ${email.category}${isArchived ? ' archived' : ''}" onclick='showEmailDetail(${JSON.stringify(email.id)})'>
                <div class="email-header">
                    <div class="email-subject">${escapeHtml(email.subject || '(No subject)')}</div>
                    <div class="email-meta">
                        <span class="email-date">${date}</span>
                        <span class="category-badge ${email.category}">${cat.label}</span>
                        ${action}
                    </div>
                </div>
                <div class="email-info">
                    <span class="email-sender">${escapeHtml(email.sender || 'Unknown')}</span>
                    ${company}${sep}${jobTitle}
                </div>
                ${email.snippet ? `<div class="email-snippet">${escapeHtml(email.snippet)}</div>` : ''}
            </div>
        `;
    }).join('');
}

function renderPagination() {
    const pagination = document.getElementById('pagination');
    if (!pagination || state.totalPages <= 1) {
        if (pagination) pagination.innerHTML = '';
        return;
    }

    pagination.innerHTML = `
        <button class="btn" onclick="setPage(${state.currentPage - 1})" ${state.currentPage <= 1 ? 'disabled' : ''}>
            ← Previous
        </button>
        <span class="page-info">
            ${state.currentPage} / ${state.totalPages}
            <span style="opacity:0.5"> (${state.totalEmails})</span>
        </span>
        <button class="btn" onclick="setPage(${state.currentPage + 1})" ${state.currentPage >= state.totalPages ? 'disabled' : ''}>
            Next →
        </button>
    `;
}

function renderSkeletons() {
    const list = document.getElementById('emailList');
    if (!list) return;
    list.innerHTML = Array(6).fill(0).map(() =>
        '<div class="skeleton skeleton-card"></div>'
    ).join('');
}

// ─── Email Detail Modal ───────────────────────────────────────────────────────
async function showEmailDetail(emailId) {
    const emailData = await api(`/api/emails/${emailId}`);
    if (!emailData || emailData.error) return;

    const cat = CATEGORIES[emailData.category] || CATEGORIES.other;
    const date = formatDate(emailData.date);

    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };

    const metaRows = [
        ['From',     escapeHtml(emailData.sender)],
        ['Date',     date],
        ['Category', `<span class="category-badge ${emailData.category}">${cat.label}</span>`],
        emailData.company_name ? ['Company',  escapeHtml(emailData.company_name)] : null,
        emailData.job_title    ? ['Position', escapeHtml(emailData.job_title)]    : null,
    ].filter(Boolean);

    overlay.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-subject">${escapeHtml(emailData.subject || '(No subject)')}</div>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">${IC.close}</button>
            </div>
            <div class="modal-meta">
                ${metaRows.map(([label, value]) => `
                    <span class="modal-meta-label">${label}</span>
                    <span class="modal-meta-value">${value}</span>
                `).join('')}
            </div>
            <div class="modal-body">${escapeHtml(emailData.body_preview || emailData.snippet || 'No preview available.')}</div>
        </div>
    `;

    document.body.appendChild(overlay);

    document.addEventListener('keydown', function onKey(e) {
        if (e.key === 'Escape') {
            overlay.remove();
            document.removeEventListener('keydown', onKey);
        }
    });
}

// ─── Toast ────────────────────────────────────────────────────────────────────
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icon = { success: IC.checkOk, error: IC.warn, info: IC.info }[type] || IC.info;
    toast.innerHTML = `${icon}<span>${escapeHtml(message)}</span>`;

    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

// ─── Utilities ────────────────────────────────────────────────────────────────
function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    try {
        const d = new Date(dateStr);
        const now = new Date();
        const diffDays = Math.floor((now - d) / 86400000);

        if (diffDays === 0) return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7)  return `${diffDays}d ago`;
        return d.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: d.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
        });
    } catch {
        return dateStr;
    }
}
