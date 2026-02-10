"""
Gmail API OAuth2 Authentication Module.
Handles the OAuth2 flow and provides a Gmail service object.
"""

import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'credentials.json')
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.json')
REDIRECT_URI = 'http://127.0.0.1:5000/api/auth/callback'


def get_auth_flow():
    """Create and return an OAuth2 flow for Gmail API."""
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
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
