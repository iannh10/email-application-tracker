# 📬 Job Application Email Tracker

A smart email tracker that connects to your Gmail, scans your inbox, and automatically classifies job-application emails into categories — rejections, interviews, offers, follow-ups, applications, and more.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.1-green?logo=flask)
![Gmail API](https://img.shields.io/badge/Gmail-API-red?logo=gmail)

---

## ✨ Features

- **Gmail OAuth2 Integration** — Securely connect your Gmail account (read-only access)
- **Smart Classification** — Multi-signal algorithm detects interview invitations, rejections, offers, follow-ups, and application confirmations
- **Auto-Scan** — Background scheduler scans every 15 minutes automatically
- **Dashboard UI** — Professional dark/light mode dashboard with stats, search, and filtering
- **Up to 2,000 emails** scanned per run
- **Noise Filtering** — Automatically filters out LinkedIn notifications, newsletters, forums, and marketing emails

## 🧠 Classification Algorithm

The classifier uses a multi-signal approach rather than simple keyword matching:

| Category | How It's Detected |
|---|---|
| **Interview** | Two-tier system: Tier 1 explicit invitations ("invite you to an interview"), Tier 2 requires subject-line keyword + action signal |
| **Offer** | Must contain language directed at the recipient ("pleased to offer you") |
| **Rejection** | Pattern-matched phrases ("decided to move forward with other candidates") |
| **Applied** | Subject-line priority for confirmation emails ("application received") |
| **Follow-up** | Requires job-context words alongside follow-up phrases |
| **Direct** | Outreach from company emails (not job boards or automated senders) |
| **Other** | Everything else — newsletters, notifications, non-job emails |

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- A Google Cloud project with Gmail API enabled
- OAuth2 credentials (`credentials.json`)

### Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/iannh10/email-application-tracker.git
   cd email-application-tracker
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Set up Google OAuth2**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the **Gmail API**
   - Create OAuth2 credentials (Desktop or Web application)
   - Download `credentials.json` and place it in the project root

4. **Run the app**
   ```bash
   python app.py
   ```
   Open [http://localhost:5000](http://localhost:5000) and click **Connect Gmail**.

## 🌐 Deployment (Render)

The app is deployment-ready with `Procfile` and `gunicorn`:

1. Push to GitHub
2. Create a new **Web Service** on [Render](https://render.com)
3. Set **Build Command**: `pip install -r requirements.txt`
4. Set **Start Command**: `gunicorn app:app`
5. Add environment variable: `GOOGLE_CREDENTIALS` = contents of your `credentials.json`
6. Add your Render URL's callback to Google Console authorized redirect URIs:
   ```
   https://your-app.onrender.com/api/auth/callback
   ```

## 📁 Project Structure

```
├── app.py                 # Flask app + API routes + auto-scan scheduler
├── gmail_auth.py          # OAuth2 authentication flow
├── email_fetcher.py       # Gmail API email fetching
├── email_classifier.py    # Multi-signal classification engine
├── database.py            # SQLite database layer
├── static/
│   ├── index.html         # Dashboard HTML
│   ├── styles.css         # Dark/light theme styles
│   └── app.js             # Frontend logic
├── Procfile               # Render deployment
├── requirements.txt       # Python dependencies
└── .gitignore
```

## 🔒 Privacy

- **Read-only** Gmail access — the app never sends, modifies, or deletes emails
- Credentials and tokens are never committed to git
- All data is stored locally in SQLite

## 📄 License

MIT
