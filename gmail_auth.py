"""
Gmail API OAuth2 Authentication Module.
Handles the OAuth2 flow and provides a Gmail service object.
Supports both local (credentials.json) and deployed (env var) credential sources.
"""

import os
import json
import tempfile
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')


def _get_redirect_uri():
    """Determine redirect URI based on environment."""
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        return f"{render_url}/api/auth/callback"
    return os.environ.get('REDIRECT_URI', 'http://127.0.0.1:5000/api/auth/callback')


def _get_credentials_file():
    """
    Get path to credentials.json.
    In production, credentials can be supplied via GOOGLE_CREDENTIALS env var
    containing the full JSON content.
    """
    # If the env var is set, write it to a temp file and return that path
    creds_json = os.environ.get('GOOGLE_CREDENTIALS')
    if creds_json:
        tmp = os.path.join(tempfile.gettempdir(), 'google_credentials.json')
        with open(tmp, 'w') as f:
            f.write(creds_json)
        return tmp
    return CREDENTIALS_FILE


def get_auth_flow():
    """Create and return an OAuth2 flow for Gmail API."""
    creds_file = _get_credentials_file()
    flow = Flow.from_client_secrets_file(
        creds_file,
        scopes=SCOPES,
        redirect_uri=_get_redirect_uri()
    )
    return flow


def get_auth_url():
    """Generate the OAuth2 authorization URL."""
    flow = get_auth_flow()
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return auth_url


def exchange_code(auth_code):
    """Exchange the authorization code for credentials and save them."""
    flow = get_auth_flow()
    flow.fetch_token(code=auth_code)
    creds = flow.credentials
    _save_token(creds)
    return creds


def _save_token(creds):
    """Save credentials to token.json."""
    token_data = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': list(creds.scopes) if creds.scopes else SCOPES
    }
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f)


def get_credentials():
    """Load credentials from token.json, refreshing if needed. Returns None if not authenticated."""
    if not os.path.exists(TOKEN_FILE):
        return None

    try:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    except Exception:
        return None

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            _save_token(creds)
        except Exception:
            os.remove(TOKEN_FILE)
            return None

    if not creds or not creds.valid:
        return None

    return creds


def get_gmail_service():
    """Build and return a Gmail API service object. Returns None if not authenticated."""
    creds = get_credentials()
    if not creds:
        return None
    return build('gmail', 'v1', credentials=creds)


def is_authenticated():
    """Check if we have valid credentials."""
    return get_credentials() is not None


def logout():
    """Remove stored credentials."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
