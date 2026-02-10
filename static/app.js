/**
 * Job Application Email Tracker — Frontend Application
 * Handles state management, API communication, and dynamic UI rendering.
 */

// ─── State ──────────────────────────────────────────────────────────────────────
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
    isLoading: true,
    theme: localStorage.getItem('theme') || 'dark',
};

// ─── Category Config ────────────────────────────────────────────────────────────
const CATEGORIES = {
    all: { label: 'All', icon: '📋', color: '#818cf8' },
    rejection: { label: 'Rejections', icon: '❌', color: '#f87171' },
    interview: { label: 'Interviews', icon: '🎯', color: '#34d399' },
    offer: { label: 'Offers', icon: '🎉', color: '#fbbf24' },
    follow_up: { label: 'Follow-ups', icon: '🔄', color: '#60a5fa' },
    applied: { label: 'Applied', icon: '📤', color: '#a78bfa' },
    direct: { label: 'Direct', icon: '💼', color: '#2dd4bf' },
    other: { label: 'Other', icon: '📧', color: '#94a3b8' },
};

// ─── API Helpers ────────────────────────────────────────────────────────────────
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

// ─── Initialization ─────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', init);

async function init() {
    // Apply saved theme
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

// ─── Actions ────────────────────────────────────────────────────────────────────
async function scanEmails() {
    if (state.isScanning) return;
    state.isScanning = true;
    renderHeaderActions();
    showToast('Scanning your Gmail for job emails... This may take a moment.', 'info');

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

// ─── Rendering ──────────────────────────────────────────────────────────────────
function renderAuthScreen() {
    const main = document.getElementById('mainContent');
    const header = document.getElementById('headerActions');
    header.innerHTML = '';

    main.innerHTML = `
        <div class="auth-screen">
            <div class="auth-card">
                <div class="auth-icon">📬</div>
                <h2>Connect Your Gmail</h2>
                <p>
                    Link your Gmail account to automatically find and categorize
                    all your job application emails — rejections, interviews,
                    offers, follow-ups, and more.
                </p>
                <a href="/api/auth" class="btn btn-google">
                    <svg width="18" height="18" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>
                    Connect Gmail Account
                </a>
            </div>
        </div>
    `;
}

function renderDashboard() {
    renderHeaderActions();
    const main = document.getElementById('mainContent');

    main.innerHTML = `
        <div class="stats-grid" id="statsGrid"></div>
        <div class="toolbar">
            <div class="search-wrapper">
                <span class="search-icon">🔍</span>
                <input
                    type="text"
                    class="search-input"
                    id="searchInput"
                    placeholder="Search by company, subject, or keyword..."
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
    const header = document.getElementById('headerActions');
    header.innerHTML = `
        <button class="theme-toggle" onclick="toggleTheme()" title="Toggle light/dark mode">
            ${state.theme === 'dark' ? '☀️' : '🌙'}
        </button>
        <button class="btn btn-primary ${state.isScanning ? 'loading' : ''}" onclick="scanEmails()" ${state.isScanning ? 'disabled' : ''}>
            <span class="spinner"></span>
            <span class="btn-text">${state.isScanning ? 'Scanning...' : '🔄 Scan Emails'}</span>
        </button>
        <button class="btn btn-danger" onclick="handleLogout()">Logout</button>
    `;
}

function renderStats() {
    const grid = document.getElementById('statsGrid');
    if (!grid) return;

    const cats = state.stats.categories || {};
    const statsData = [
        { key: 'total', label: 'Total Emails', value: state.stats.total || 0, icon: '📊' },
        { key: 'rejection', label: 'Rejections', value: cats.rejection || 0, icon: '✕' },
        { key: 'interview', label: 'Interviews', value: cats.interview || 0, icon: '🎯' },
        { key: 'offer', label: 'Offers', value: cats.offer || 0, icon: '⭐' },
        { key: 'follow_up', label: 'Follow-ups', value: cats.follow_up || 0, icon: '↻' },
        { key: 'applied', label: 'Applied', value: cats.applied || 0, icon: '📤' },
        { key: 'direct', label: 'Direct', value: cats.direct || 0, icon: '💼' },
    ];

    grid.innerHTML = statsData.map(s => `
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
        const count = key === 'all' ? total : (cats[key] || 0);
        const active = state.currentCategory === key ? 'active' : '';
        return `
            <button class="tab-btn ${active}" onclick="setCategory('${key}')">
                ${conf.icon} ${conf.label}
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
                <div class="empty-icon">${state.searchQuery ? '🔍' : '📭'}</div>
                <h3>${state.searchQuery ? 'No emails match your search' : 'No emails found'}</h3>
                <p>${state.searchQuery
                ? 'Try a different search term or clear your filters.'
                : 'Click "Scan Emails" to fetch and classify your job application emails from Gmail.'
            }</p>
            </div>
        `;
        return;
    }

    list.innerHTML = state.emails.map(email => {
        const cat = CATEGORIES[email.category] || CATEGORIES.other;
        const date = formatDate(email.date);
        const company = email.company_name ? `<span class="email-company">${escapeHtml(email.company_name)}</span>` : '';
        const jobTitle = email.job_title ? `<span class="email-job-title">${escapeHtml(email.job_title)}</span>` : '';
        const sep = company && jobTitle ? '<span style="color:var(--text-muted);opacity:0.4">·</span>' : '';

        return `
            <div class="email-card ${email.category}" onclick='showEmailDetail(${JSON.stringify(email.id)})'>
                <div class="email-header">
                    <div class="email-subject">${escapeHtml(email.subject || '(No subject)')}</div>
                    <div class="email-meta">
                        <span class="email-date">${date}</span>
                        <span class="category-badge ${email.category}">${cat.label}</span>
                    </div>
                </div>
                <div class="email-info">
                    <span class="email-sender">${escapeHtml(email.sender || 'Unknown')}</span>
                    ${company}${sep}${jobTitle}
                </div>
                <div class="email-snippet">${escapeHtml(email.snippet || '')}</div>
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
            Page ${state.currentPage} of ${state.totalPages}
            (${state.totalEmails} emails)
        </span>
        <button class="btn" onclick="setPage(${state.currentPage + 1})" ${state.currentPage >= state.totalPages ? 'disabled' : ''}>
            Next →
        </button>
    `;
}

function renderSkeletons() {
    const list = document.getElementById('emailList');
    if (!list) return;
    list.innerHTML = Array(5).fill(0).map(() =>
        '<div class="skeleton skeleton-card"></div>'
    ).join('');
}

// ─── Email Detail Modal ─────────────────────────────────────────────────────────
async function showEmailDetail(emailId) {
    const emailData = await api(`/api/emails/${emailId}`);
    if (!emailData || emailData.error) return;

    const cat = CATEGORIES[emailData.category] || CATEGORIES.other;
    const date = formatDate(emailData.date);

    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };

    overlay.innerHTML = `
        <div class="modal-content">
            <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">✕</button>
            <div class="modal-subject">${escapeHtml(emailData.subject || '(No subject)')}</div>
            <div class="modal-meta">
                <div class="modal-meta-item"><strong>From:</strong> ${escapeHtml(emailData.sender)}</div>
                <div class="modal-meta-item"><strong>Date:</strong> ${date}</div>
                <div class="modal-meta-item"><strong>Category:</strong>
                    <span class="category-badge ${emailData.category}">${cat.icon} ${cat.label}</span>
                </div>
                ${emailData.company_name ? `<div class="modal-meta-item"><strong>Company:</strong> ${escapeHtml(emailData.company_name)}</div>` : ''}
                ${emailData.job_title ? `<div class="modal-meta-item"><strong>Position:</strong> ${escapeHtml(emailData.job_title)}</div>` : ''}
            </div>
            <div class="modal-body">${escapeHtml(emailData.body_preview || emailData.snippet || 'No preview available.')}</div>
        </div>
    `;

    document.body.appendChild(overlay);
}

// ─── Toast Notifications ────────────────────────────────────────────────────────
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = { success: '✅', error: '⚠️', info: 'ℹ️' };
    toast.innerHTML = `<span>${icons[type] || ''}</span> ${escapeHtml(message)}`;

    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

// ─── Utilities ──────────────────────────────────────────────────────────────────
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
        const diffMs = now - d;
        const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

        if (diffDays === 0) {
            return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
        } else if (diffDays === 1) {
            return 'Yesterday';
        } else if (diffDays < 7) {
            return `${diffDays}d ago`;
        } else {
            return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: d.getFullYear() !== now.getFullYear() ? 'numeric' : undefined });
        }
    } catch {
        return dateStr;
    }
}
