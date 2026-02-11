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
from database import init_db, upsert_email, get_emails, get_stats, get_email_by_id

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
        max_results = request.json.get('max_results', 2000) if request.json else 2000
        raw_emails = fetch_emails(max_results=max_results)
        classified = classify_emails(raw_emails)

        count = 0
        for email in classified:
            upsert_email(email)
            count += 1

        return jsonify({
            'success': True,
            'emails_processed': count,
            'message': f'Successfully scanned and classified {count} emails.'
        })
    except Exception as e:
        return jsonify({'error': f'Scan failed: {str(e)}'}), 500


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
    port = int(os.environ.get('PORT', 5000))
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║     Job Application Email Tracker                   ║")
    print(f"║     Open: http://localhost:{port}                      ║")
    print("╚══════════════════════════════════════════════════════╝\n")
    app.run(debug=True, port=port)

