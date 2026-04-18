"""
Job Application Email Tracker — Flask Application.
Main entry point with API endpoints and OAuth callback handling.
"""

import os
import threading
from datetime import datetime, timezone
from flask import Flask, request, jsonify, redirect, send_from_directory
from gmail_auth import get_auth_url, exchange_code, is_authenticated, logout
from email_fetcher import fetch_emails
from email_classifier import classify_emails
from database import (
    init_db, upsert_email, get_emails, get_stats, get_email_by_id,
    reclassify_all, get_all_ids, set_archived, archive_by_category,
    unarchive_all, delete_older_than,
)

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.urandom(24)



# ─── Static Routes ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


# ─── Auth Routes ─────────────────────────────────────────────────────────────────

@app.route('/api/auth/status')
def auth_status():
    """Check if the user is authenticated."""
    return jsonify({'authenticated': is_authenticated()})


@app.route('/api/auth')
def auth():
    """Start OAuth2 flow — redirects to Google."""
    try:
        url = get_auth_url()
        return redirect(url)
    except FileNotFoundError:
        return jsonify({
            'error': 'credentials.json not found. Please download OAuth2 credentials from Google Cloud Console.'
        }), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/callback')
def auth_callback():
    """Handle OAuth2 callback from Google."""
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No authorization code received'}), 400

    try:
        exchange_code(code)
        return redirect('/')
    except Exception as e:
        return jsonify({'error': f'Authentication failed: {str(e)}'}), 500


@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    """Logout and remove stored credentials."""
    logout()
    return jsonify({'success': True})


# ─── Email Routes ────────────────────────────────────────────────────────────────

@app.route('/api/scan', methods=['POST'])
def scan_emails():
    """Trigger a fresh email scan from Gmail."""
    if not is_authenticated():
        return jsonify({'error': 'Not authenticated. Please connect Gmail first.'}), 401

    try:
        max_results = request.json.get('max_results', 5000) if request.json else 5000
        print(f"[Scan] Starting scan (max {max_results} matching emails)")

        known_ids = get_all_ids()

        def _progress(done, total):
            print(f"[Scan]   downloaded {done}/{total} new emails…")

        raw_emails = fetch_emails(
            max_results=max_results,
            known_ids=known_ids,
            progress=_progress,
        )
        print(f"[Scan] Classifying {len(raw_emails)} new emails…")
        classified = classify_emails(raw_emails)

        counts = {}
        for email in classified:
            upsert_email(email)
            cat = email.get('category', 'other')
            counts[cat] = counts.get(cat, 0) + 1

        new_count = sum(counts.values())

        if new_count == 0:
            msg = 'No new emails found — your inbox is up to date.'
            print(f"[Scan] Done. {msg}")
            return jsonify({
                'success': True,
                'emails_processed': 0,
                'breakdown': {},
                'message': msg,
            })

        summary = ', '.join(f"{c} {k}" for k, c in sorted(counts.items(), key=lambda x: -x[1]))
        print(f"[Scan] Done. Added {new_count} new emails — {summary}")

        return jsonify({
            'success': True,
            'emails_processed': new_count,
            'breakdown': counts,
            'message': f'Added {new_count} new emails ({summary}).'
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Scan failed: {str(e)}'}), 500


@app.route('/api/reclassify', methods=['POST'])
def reclassify_emails():
    """Re-run classification on all emails already in the DB (no Gmail fetch)."""
    try:
        from email_classifier import classify_email
        print("[Reclassify] Re-running classifier on all stored emails…")
        result = reclassify_all(classify_email)
        diff_str = ', '.join(f"{k}: {v}" for k, v in result['diff'].items()) or 'no changes'
        print(f"[Reclassify] Done. {result['changed']}/{result['total']} emails updated ({diff_str})")
        return jsonify({
            'success': True,
            'total': result['total'],
            'changed': result['changed'],
            'diff': result['diff'],
            'message': f"Re-classified {result['total']} emails — {result['changed']} categorizations updated."
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Reclassify failed: {str(e)}'}), 500


@app.route('/api/emails')
def list_emails():
    """List emails with optional filtering."""
    category = request.args.get('category', 'all')
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))

    result = get_emails(
        category=category,
        search=search,
        page=page,
        per_page=per_page
    )
    return jsonify(result)


@app.route('/api/emails/<email_id>')
def get_single_email(email_id):
    """Get a single email by ID."""
    email = get_email_by_id(email_id)
    if email:
        return jsonify(email)
    return jsonify({'error': 'Email not found'}), 404


@app.route('/api/stats')
def stats():
    """Get dashboard statistics."""
    return jsonify(get_stats())


# ─── Archive / Cleanup Routes ────────────────────────────────────────────────

@app.route('/api/emails/<email_id>/archive', methods=['POST'])
def archive_single(email_id):
    """Archive a single email."""
    changed = set_archived(email_id, archived=True)
    return jsonify({'success': bool(changed)})


@app.route('/api/emails/<email_id>/unarchive', methods=['POST'])
def unarchive_single(email_id):
    """Unarchive a single email."""
    changed = set_archived(email_id, archived=False)
    return jsonify({'success': bool(changed)})


@app.route('/api/archive/bulk', methods=['POST'])
def archive_bulk():
    """Archive every active email in a given category (default: 'rejection')."""
    category = (request.json or {}).get('category', 'rejection')
    count = archive_by_category(category)
    return jsonify({
        'success': True,
        'count': count,
        'message': f'Archived {count} {category} emails.',
    })


@app.route('/api/archive/restore', methods=['POST'])
def archive_restore():
    """Restore every archived email to the active view."""
    count = unarchive_all()
    return jsonify({
        'success': True,
        'count': count,
        'message': f'Restored {count} archived emails.',
    })


@app.route('/api/cleanup', methods=['POST'])
def cleanup_old():
    """Delete emails older than `days` days, optionally filtered by categories."""
    data = request.json or {}
    days = int(data.get('days', 180))
    categories = data.get('categories')
    if isinstance(categories, str):
        categories = [categories]

    deleted = delete_older_than(days=days, categories=categories, include_archived=True)
    label = f"older than {days} days"
    if categories:
        label += f" in [{', '.join(categories)}]"
    print(f"[Cleanup] Deleted {deleted} emails {label}")
    return jsonify({
        'success': True,
        'deleted': deleted,
        'message': f'Deleted {deleted} emails {label}.',
    })


# ─── Auto-Scan Scheduler ─────────────────────────────────────────────────────────

AUTO_SCAN_INTERVAL = int(os.environ.get('AUTO_SCAN_INTERVAL', 900))  # 15 min default

auto_scan_status = {
    'last_scan': None,
    'next_scan': None,
    'last_result': None,
    'is_running': False,
}

_scheduler_timer = None


def _run_auto_scan():
    """Background task: scan and classify emails if authenticated."""
    global _scheduler_timer
    auto_scan_status['is_running'] = True

    try:
        if is_authenticated():
            print(f"[Auto-Scan] Starting scheduled scan at {datetime.now(timezone.utc).isoformat()}")
            raw = fetch_emails(max_results=2000)
            classified = classify_emails(raw)
            count = 0
            for email in classified:
                upsert_email(email)
                count += 1
            auto_scan_status['last_scan'] = datetime.now(timezone.utc).isoformat()
            auto_scan_status['last_result'] = f'Scanned {count} emails'
            print(f"[Auto-Scan] Done — processed {count} emails.")
        else:
            auto_scan_status['last_result'] = 'Skipped (not authenticated)'
            print("[Auto-Scan] Skipped — user not authenticated.")
    except Exception as e:
        auto_scan_status['last_result'] = f'Error: {str(e)}'
        print(f"[Auto-Scan] Error: {e}")
    finally:
        auto_scan_status['is_running'] = False
        # Schedule next run
        _scheduler_timer = threading.Timer(AUTO_SCAN_INTERVAL, _run_auto_scan)
        _scheduler_timer.daemon = True
        _scheduler_timer.start()
        auto_scan_status['next_scan'] = datetime.now(timezone.utc).isoformat()


def start_scheduler():
    """Start the background auto-scan scheduler."""
    global _scheduler_timer
    # Run first scan after a short delay (let the app boot)
    _scheduler_timer = threading.Timer(10, _run_auto_scan)
    _scheduler_timer.daemon = True
    _scheduler_timer.start()
    print(f"[Auto-Scan] Scheduler started — scanning every {AUTO_SCAN_INTERVAL // 60} minutes.")


@app.route('/api/autoscan/status')
def autoscan_status():
    """Get the auto-scan scheduler status."""
    return jsonify({
        'enabled': True,
        'interval_minutes': AUTO_SCAN_INTERVAL // 60,
        **auto_scan_status,
    })


# ─── Main ────────────────────────────────────────────────────────────────────────

# Initialize the database at import time (needed for gunicorn in production)
init_db()

# Start the auto-scan scheduler (only once, avoid double-start in debug reloader)
if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not os.environ.get('WERKZEUG_SERVER_FD'):
    start_scheduler()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║     Job Application Email Tracker                   ║")
    print(f"║     Open: http://localhost:{port}                      ║")
    print("╚══════════════════════════════════════════════════════╝\n")
    app.run(debug=True, port=port)

