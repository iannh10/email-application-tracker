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
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
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


def get_emails(category=None, search=None, page=1, per_page=50):
    """Get emails with optional filtering and pagination."""
    conn = get_connection()
    cursor = conn.cursor()

    query = 'SELECT * FROM emails WHERE 1=1'
    params = []

    if category and category != 'all':
        query += ' AND category = ?'
        params.append(category)

    if search:
        query += ' AND (subject LIKE ? OR company_name LIKE ? OR sender LIKE ? OR snippet LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term] * 4)

    # Get total count
    count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]

    # Add ordering and pagination
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
    """Get email statistics by category."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as total FROM emails')
    total = cursor.fetchone()['total']

    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM emails
        GROUP BY category
        ORDER BY count DESC
    ''')
    categories = {row['category']: row['count'] for row in cursor.fetchall()}

    # Recent emails (last 7 days)
    cursor.execute('''
        SELECT COUNT(*) as recent
        FROM emails
        WHERE date >= datetime('now', '-7 days')
    ''')
    recent = cursor.fetchone()['recent']

    conn.close()
    return {
        'total': total,
        'categories': categories,
        'recent_7_days': recent
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
