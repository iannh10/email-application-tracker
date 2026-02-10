"""
Email Fetcher Module.
Fetches job-related emails from Gmail API and parses them into structured data.
"""

import base64
import re
from datetime import datetime
from bs4 import BeautifulSoup
from email.utils import parsedate_to_datetime
from gmail_auth import get_gmail_service


# Job board and ATS domains to search
JOB_DOMAINS = [
    'indeed.com', 'linkedin.com', 'greenhouse.io', 'lever.co',
    'myworkday.com', 'myworkdayjobs.com', 'workday.com',
    'smartrecruiters.com', 'icims.com', 'jobvite.com',
    'applytojob.com', 'ashbyhq.com', 'breezy.hr',
    'recruitee.com', 'jazz.co', 'bamboohr.com',
    'taleo.net', 'successfactors.com', 'ultipro.com',
    'paylocity.com', 'paycom.com', 'adp.com',
    'hire.lever.co', 'boards.greenhouse.io',
    'jobs.lever.co', 'app.dover.io',
    'rippling.com', 'gusto.com',
]

# Keywords to search in email subjects/bodies
JOB_KEYWORDS = [
    'application', 'applied', 'interview', 'offer letter',
    'we regret', 'unfortunately', 'move forward',
    'candidacy', 'candidate', 'position', 'role',
    'hiring', 'recruiter', 'recruitment', 'talent',
    'job opportunity', 'next steps', 'phone screen',
    'onsite', 'technical interview', 'hiring manager',
    'thank you for your interest', 'application status',
    'we have reviewed', 'your application',
]


def build_search_query(max_results=500):
    """Build Gmail search query for job-related emails."""
    domain_queries = [f'from:{domain}' for domain in JOB_DOMAINS]
    keyword_queries = [f'subject:"{kw}"' for kw in [
        'application', 'interview', 'offer', 'position',
        'candidacy', 'your application', 'applied',
        'we regret', 'next steps', 'recruitment',
        'hiring', 'recruiter', 'talent acquisition',
    ]]

    # Combine: emails from job domains OR with job keywords in subject
    query = f'({" OR ".join(domain_queries)} OR {" OR ".join(keyword_queries)})'
    # Only look at inbox and updates, skip spam/trash
    query += ' -in:spam -in:trash'
    return query


def fetch_emails(max_results=1000):
    """Fetch job-related emails from Gmail."""
    service = get_gmail_service()
    if not service:
        return []

    query = build_search_query()
    emails = []
    page_token = None

    while len(emails) < max_results:
        try:
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=min(100, max_results - len(emails)),
                pageToken=page_token
            ).execute()
        except Exception as e:
            print(f"Error fetching email list: {e}")
            break

        messages = results.get('messages', [])
        if not messages:
            break

        for msg_meta in messages:
            email_data = _fetch_single_email(service, msg_meta['id'])
            if email_data:
                emails.append(email_data)

        page_token = results.get('nextPageToken')
        if not page_token:
            break

    return emails


def _fetch_single_email(service, msg_id):
    """Fetch and parse a single email by ID."""
    try:
        msg = service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()
    except Exception as e:
        print(f"Error fetching email {msg_id}: {e}")
        return None

    headers = {h['name'].lower(): h['value'] for h in msg['payload'].get('headers', [])}

    sender = headers.get('from', '')
    subject = headers.get('subject', '')
    date_str = headers.get('date', '')

    # Parse date
    date = _parse_date(date_str)

    # Extract sender info
    sender_email = _extract_email_address(sender)
    sender_domain = _extract_domain(sender_email)
    sender_name = _extract_sender_name(sender)

    # Get body
    body = _get_body(msg['payload'])
    body_text = _html_to_text(body) if body else ''

    # Truncate body preview
    body_preview = body_text[:500] if body_text else ''

    snippet = msg.get('snippet', '')

    return {
        'id': msg_id,
        'subject': subject,
        'sender': sender,
        'sender_email': sender_email,
        'sender_domain': sender_domain,
        'sender_name': sender_name,
        'date': date,
        'snippet': snippet,
        'body_text': body_text,
        'body_preview': body_preview,
    }


def _parse_date(date_str):
    """Parse email date string to ISO format."""
    if not date_str:
        return datetime.utcnow().isoformat()
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.isoformat()
    except Exception:
        return date_str


def _extract_email_address(sender):
    """Extract email address from 'Name <email>' format."""
    match = re.search(r'<([^>]+)>', sender)
    if match:
        return match.group(1).lower()
    if '@' in sender:
        return sender.strip().lower()
    return sender


def _extract_domain(email):
    """Extract domain from email address."""
    if '@' in email:
        return email.split('@')[1]
    return ''


def _extract_sender_name(sender):
    """Extract display name from sender field."""
    match = re.match(r'^"?([^"<]+)"?\s*<', sender)
    if match:
        return match.group(1).strip()
    return sender.split('@')[0] if '@' in sender else sender


def _get_body(payload):
    """Recursively extract email body from payload."""
    body = ''

    if 'body' in payload and payload['body'].get('data'):
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='replace')
        return body

    parts = payload.get('parts', [])

    # Prefer HTML, then plain text
    html_body = ''
    text_body = ''

    for part in parts:
        mime_type = part.get('mimeType', '')

        if mime_type == 'text/html' and part.get('body', {}).get('data'):
            html_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='replace')
        elif mime_type == 'text/plain' and part.get('body', {}).get('data'):
            text_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='replace')
        elif mime_type.startswith('multipart/'):
            nested = _get_body(part)
            if nested:
                return nested

    return html_body or text_body


def _html_to_text(html):
    """Convert HTML to plain text."""
    if not html:
        return ''
    try:
        soup = BeautifulSoup(html, 'html.parser')
        # Remove script and style elements
        for tag in soup(['script', 'style', 'head']):
            tag.decompose()
        text = soup.get_text(separator=' ', strip=True)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception:
        return html
