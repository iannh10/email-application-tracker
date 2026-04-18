"""
SQLite Database Layer for Job Email Tracker.
Handles schema creation and CRUD operations for email records.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'job_tracker.db')


def get_connection():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            subject TEXT,
            sender TEXT,
            sender_domain TEXT,
            date TEXT,
            category TEXT,
            confidence REAL,
            company_name TEXT,
            job_title TEXT,
            snippet TEXT,
            body_preview TEXT,
            is_read INTEGER DEFAULT 0,
            is_archived INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Migrate: add is_archived column if it doesn't exist on old DBs
    cursor.execute("PRAGMA table_info(emails)")
    columns = {row[1] for row in cursor.fetchall()}
    if 'is_archived' not in columns:
        cursor.execute('ALTER TABLE emails ADD COLUMN is_archived INTEGER DEFAULT 0')
    conn.commit()
    conn.close()


def upsert_email(email_data):
    """Insert or update an email record."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO emails (id, subject, sender, sender_domain, date, category,
                           confidence, company_name, job_title, snippet, body_preview, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            category = excluded.category,
            confidence = excluded.confidence,
            company_name = excluded.company_name,
            job_title = excluded.job_title
    ''', (
        email_data.get('id'),
        email_data.get('subject', ''),
        email_data.get('sender', ''),
        email_data.get('sender_domain', ''),
        email_data.get('date', ''),
        email_data.get('category', 'unknown'),
        email_data.get('confidence', 0.0),
        email_data.get('company_name', ''),
        email_data.get('job_title', ''),
        email_data.get('snippet', ''),
        email_data.get('body_preview', ''),
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    conn.close()


def get_emails(category=None, search=None, page=1, per_page=50, include_archived=False):
    """Get emails with optional filtering and pagination.

    By default archived emails are hidden. Pass category='archived' to view
    archived-only, or include_archived=True to include them alongside active.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = 'SELECT * FROM emails WHERE 1=1'
    params = []

    if category == 'archived':
        query += ' AND is_archived = 1'
    elif not include_archived:
        query += ' AND (is_archived IS NULL OR is_archived = 0)'

    if category and category not in ('all', 'archived'):
        query += ' AND category = ?'
        params.append(category)

    if search:
        query += ' AND (subject LIKE ? OR company_name LIKE ? OR sender LIKE ? OR snippet LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term] * 4)

    count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]

    query += ' ORDER BY date DESC LIMIT ? OFFSET ?'
    params.extend([per_page, (page - 1) * per_page])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    emails = [dict(row) for row in rows]

    conn.close()
    return {
        'emails': emails,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': max(1, (total + per_page - 1) // per_page)
    }


def get_stats():
    """Get email statistics by category. Counts exclude archived emails."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as total FROM emails WHERE is_archived IS NULL OR is_archived = 0')
    total = cursor.fetchone()['total']

    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM emails
        WHERE is_archived IS NULL OR is_archived = 0
        GROUP BY category
        ORDER BY count DESC
    ''')
    categories = {row['category']: row['count'] for row in cursor.fetchall()}

    cursor.execute('''
        SELECT COUNT(*) as recent
        FROM emails
        WHERE (is_archived IS NULL OR is_archived = 0)
          AND date >= datetime('now', '-7 days')
    ''')
    recent = cursor.fetchone()['recent']

    cursor.execute('SELECT COUNT(*) as archived FROM emails WHERE is_archived = 1')
    archived = cursor.fetchone()['archived']

    conn.close()
    return {
        'total': total,
        'categories': categories,
        'recent_7_days': recent,
        'archived': archived,
    }


def get_email_by_id(email_id):
    """Get a single email by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM emails WHERE id = ?', (email_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def mark_as_read(email_id):
    """Mark an email as read."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE emails SET is_read = 1 WHERE id = ?', (email_id,))
    conn.commit()
    conn.close()


def get_all_ids():
    """Return a set of all email IDs currently in the DB (for fast skip-lookup)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM emails')
    ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    return ids


def set_archived(email_id, archived=True):
    """Archive or unarchive a single email."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE emails SET is_archived = ? WHERE id = ?',
                   (1 if archived else 0, email_id))
    changed = cursor.rowcount
    conn.commit()
    conn.close()
    return changed


def archive_by_category(category):
    """Archive every active email in a given category. Returns count archived."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE emails SET is_archived = 1 WHERE category = ? AND (is_archived IS NULL OR is_archived = 0)',
        (category,),
    )
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count


def unarchive_all():
    """Restore all archived emails. Returns count unarchived."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE emails SET is_archived = 0 WHERE is_archived = 1')
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count


def delete_older_than(days, categories=None, include_archived=True):
    """
    Delete emails older than N days. Optionally restricted to specific
    categories. By default also removes archived emails.
    Returns dict with deleted count.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = "DELETE FROM emails WHERE date < datetime('now', ?)"
    params = [f'-{int(days)} days']

    if categories:
        placeholders = ','.join('?' * len(categories))
        query += f' AND category IN ({placeholders})'
        params.extend(categories)

    if not include_archived:
        query += ' AND (is_archived IS NULL OR is_archived = 0)'

    cursor.execute(query, params)
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted


def reclassify_all(classify_fn):
    """
    Re-run classification on every email already in the DB. Does NOT re-fetch
    from Gmail. Returns (total, changed, category_diff).

    `classify_fn` takes an email_data dict and returns a dict with at least
    'category', 'confidence', 'company_name', 'job_title'.
    """
    import re as _re

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, subject, sender, sender_domain, snippet, body_preview, category
        FROM emails
    ''')
    rows = cursor.fetchall()

    total = len(rows)
    changed = 0
    category_diff = {}

    for row in rows:
        sender = row['sender'] or ''

        m = _re.search(r'<([^>]+)>', sender)
        sender_email = (m.group(1) if m else sender).strip().lower() if '@' in sender else ''
        name_m = _re.match(r'^"?([^"<]+)"?\s*<', sender)
        sender_name = name_m.group(1).strip() if name_m else (sender.split('@')[0] if '@' in sender else sender)

        email_data = {
            'id':            row['id'],
            'subject':       row['subject'] or '',
            'sender':        sender,
            'sender_email':  sender_email,
            'sender_domain': row['sender_domain'] or '',
            'sender_name':   sender_name,
            'snippet':       row['snippet'] or '',
            'body_text':     row['body_preview'] or '',
        }

        result = classify_fn(email_data)
        new_cat = result.get('category', 'other')
        old_cat = row['category']

        if new_cat != old_cat:
            changed += 1
            key = f"{old_cat} → {new_cat}"
            category_diff[key] = category_diff.get(key, 0) + 1

        cursor.execute(
            'UPDATE emails SET category = ?, confidence = ?, company_name = ?, job_title = ? WHERE id = ?',
            (new_cat, result.get('confidence', 0.0),
             result.get('company_name', ''), result.get('job_title', ''),
             row['id'])
        )

    conn.commit()
    conn.close()
    return {'total': total, 'changed': changed, 'diff': category_diff}
