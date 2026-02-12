# Job Application Email Tracker

A Gmail-integrated tool that scans your inbox and classifies job-application emails into categories: rejections, interviews, offers, follow-ups, and applications.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-green?logo=flask)
![Gmail API](https://img.shields.io/badge/Gmail-API-red?logo=gmail)

---

## Features

- **Gmail OAuth2** — Secure read-only access to your inbox
- **Multi-signal classification** — Two-tier algorithm using sender origin, subject-line analysis, and directed language detection
- **Auto-scan** — Background scheduler runs every 15 minutes
- **Dashboard** — Dark/light mode UI with stats, search, and category filtering
- **Noise filtering** — Automatically excludes LinkedIn notifications, newsletters, forums, and marketing emails
- **Scans up to 2,000 emails** per run

## Classification

| Category | Detection Method |
|---|---|
| Interview | Tier 1: explicit invitations ("invite you to an interview"). Tier 2: subject-line keyword + action signal |
| Offer | Directed language only ("pleased to offer you") |
| Rejection | Pattern-matched phrases ("decided to move forward with other candidates") |
| Applied | Subject-line priority for confirmations ("application received") |
| Follow-up | Follow-up phrase + job-context words (application, candidacy, position) |
| Direct | Company email outreach (excludes job boards and automated senders) |
| Other | Non-job emails — newsletters, notifications, social |

## Setup

### Prerequisites
- Python 3.9+
- Google Cloud project with Gmail API enabled
- OAuth2 credentials (`credentials.json`)

### Installation

```bash
git clone https://github.com/iannh10/email-application-tracker.git
cd email-application-tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Place your `credentials.json` in the project root, then:

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) and connect your Gmail account.

## Deployment (Render)

1. Create a **Web Service** on [Render](https://render.com) and connect the repo
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn app:app`
4. Environment variable: `GOOGLE_CREDENTIALS` = contents of `credentials.json`
5. Add authorized redirect URI in Google Console:
   ```
   https://your-app.onrender.com/api/auth/callback
   ```

## Project Structure

```
app.py                 Flask app, API routes, auto-scan scheduler
gmail_auth.py          OAuth2 authentication
email_fetcher.py       Gmail API fetching
email_classifier.py    Multi-signal classification engine
database.py            SQLite storage
static/                Frontend (HTML, CSS, JS)
Procfile               Render deployment config
```

## Privacy

- Read-only Gmail access — emails are never sent, modified, or deleted
- Credentials and tokens excluded from version control
- Data stored locally in SQLite

## License

MIT
