"""
Email Classification Engine.
Classifies job-related emails into categories based on pattern matching.
"""

import re

# ─── Classification Patterns ───────────────────────────────────────────────────
# Each pattern list is ordered by specificity. We match against subject + body.

REJECTION_PATTERNS = [
    (r'we\s+have\s+decided\s+to\s+(move|proceed)\s+forward\s+with\s+other', 0.95),
    (r'we\s+will\s+not\s+be\s+(moving|going)\s+forward', 0.95),
    (r'after\s+careful\s+(consideration|review).*not\s+(moving|proceeding)', 0.93),
    (r'unfortunately.*not\s+(be\s+)?(moving|proceeding|advancing)\s+forward', 0.93),
    (r'we\s+regret\s+to\s+inform\s+you', 0.92),
    (r'we\s+are\s+unable\s+to\s+offer\s+you', 0.92),
    (r'your\s+application.*not\s+been\s+selected', 0.90),
    (r'not\s+(be\s+)?moving\s+forward\s+with\s+your', 0.90),
    (r'we\'ve\s+decided\s+to\s+pursue\s+other\s+candidates', 0.90),
    (r'decided\s+not\s+to\s+move\s+forward', 0.90),
    (r'position\s+has\s+been\s+filled', 0.88),
    (r'role\s+has\s+been\s+filled', 0.88),
    (r'we\s+have\s+chosen\s+to\s+move\s+forward\s+with\s+another', 0.88),
    (r'not\s+the\s+right\s+fit', 0.82),
    (r'we\s+won\'t\s+be\s+(moving|proceeding)', 0.85),
    (r'your\s+candidacy.*will\s+not', 0.85),
    (r'we\s+have\s+filled\s+(the|this)\s+(position|role)', 0.88),
    (r'no\s+longer\s+(considering|pursuing)', 0.85),
    (r'unable\s+to\s+move\s+forward', 0.85),
    (r'not\s+a\s+(good\s+)?match\s+(for|at)\s+this\s+time', 0.80),
    (r'will\s+not\s+be\s+extending\s+an\s+offer', 0.92),
]

INTERVIEW_PATTERNS = [
    # ── Explicit interview / screening invitations only ──
    (r'schedule\s+(an?\s+)?interview', 0.95),
    (r'interview\s+invitation', 0.95),
    (r'invite\s+you\s+to\s+(an?\s+)?interview', 0.95),
    (r'we\'d\s+like\s+to\s+invite\s+you', 0.93),
    (r'like\s+to\s+(schedule|set\s+up|arrange)\s+(a\s+)?(interview|screen)', 0.93),
    (r'phone\s+screen', 0.90),
    (r'phone\s+interview', 0.90),
    (r'video\s+interview', 0.90),
    (r'virtual\s+interview', 0.90),
    (r'onsite\s+interview', 0.92),
    (r'on-site\s+interview', 0.92),
    (r'technical\s+interview', 0.92),
    (r'coding\s+(challenge|assessment|interview)', 0.88),
    (r'next\s+round\s+(of\s+)?interview', 0.88),
    (r'next\s+step(s)?\s+in\s+(the|our)\s+interview', 0.88),
    (r'meet\s+(with\s+)?(the|our)\s+hiring\s+manager', 0.85),
    (r'recruiter\s+screen', 0.88),
    (r'panel\s+interview', 0.92),
    (r'case\s+(study|interview)', 0.85),
    (r'take-home\s+(assignment|assessment|project)', 0.88),
    (r'assessment\s+(link|invitation|test)', 0.85),
    (r'hackerrank|codility|leetcode|codesignal', 0.85),
    (r'moved\s+(you\s+)?forward\s+to\s+(the|an?)\s+(interview|screen)', 0.92),
    (r'advance(d)?\s+(you\s+)?to\s+(the|an?)\s+(interview|next)\s+(round|stage|step)', 0.90),
    (r'selected\s+for\s+(an?\s+)?interview', 0.92),
]

OFFER_PATTERNS = [
    (r'(pleased|happy|excited)\s+to\s+(extend|offer|present)', 0.95),
    (r'offer\s+letter', 0.95),
    (r'offer\s+of\s+employment', 0.95),
    (r'formal\s+offer', 0.93),
    (r'job\s+offer', 0.93),
    (r'compensation\s+(package|details)', 0.85),
    (r'(annual|base)\s+salary', 0.85),
    (r'start\s+date', 0.75),
    (r'welcome\s+to\s+the\s+team', 0.88),
    (r'we\s+would\s+like\s+to\s+offer\s+you', 0.95),
    (r'contingent\s+offer', 0.90),
    (r'background\s+check.*offer', 0.82),
    (r'sign\s+(the|your)\s+offer', 0.92),
    (r'accept\s+(the|this|our)\s+offer', 0.90),
]

FOLLOWUP_PATTERNS = [
    (r'checking\s+in\s+(on|about|regarding)', 0.82),
    (r'following\s+up\s+(on|about|regarding)', 0.82),
    (r'status\s+(update|of\s+your)', 0.80),
    (r'update\s+(on|regarding)\s+(your|the)\s+(application|candidacy|status)', 0.85),
    (r'where\s+(are\s+)?(you|things)\s+in\s+the\s+process', 0.78),
    (r'wanted\s+to\s+(follow\s+up|check\s+in|touch\s+base)', 0.80),
    (r'any\s+(update|news)\s+(on|about|regarding)', 0.75),
    (r'still\s+(interested|considering)', 0.75),
    (r'keep\s+you\s+(updated|informed|posted)', 0.72),
    (r'we\s+are\s+still\s+(reviewing|processing)', 0.78),
    (r'your\s+application\s+is\s+(still\s+)?(being|under)\s+(reviewed|consideration)', 0.82),
    (r'timeline\s+(for|on|regarding)\s+(the|this|our)', 0.72),
]

APPLIED_PATTERNS = [
    (r'(thank\s+you|thanks)\s+for\s+(your\s+)?(applying|application|interest)', 0.92),
    (r'application\s+(received|confirmed|submitted|has\s+been)', 0.94),
    (r'we\s+(have\s+)?received\s+your\s+application', 0.94),
    (r'successfully\s+(applied|submitted)', 0.92),
    (r'your\s+application\s+(for|to|has)', 0.85),
    (r'confirm.*application', 0.82),
    (r'application\s+confirmation', 0.92),
    (r'you\s+(have\s+)?(successfully\s+)?applied\s+(for|to)', 0.90),
    (r'application\s+(is\s+)?(being|under)\s+(reviewed|review|consideration)', 0.88),
    (r'we\s+will\s+(review|look\s+over)\s+your\s+(application|resume|materials)', 0.88),
    (r'your\s+(application|submission)\s+has\s+been\s+(received|submitted)', 0.94),
    (r'we\s+appreciate\s+your\s+interest\s+(in|at)', 0.85),
    (r'your\s+resume\s+(has\s+been|was)\s+(received|submitted)', 0.90),
    (r'you\s+(have\s+)?applied\s+(to|for)\s+(the|a|this)', 0.88),
]

# Known no-reply / automated senders from job boards
JOB_BOARD_DOMAINS = {
    'indeed.com', 'linkedin.com', 'greenhouse.io', 'lever.co',
    'myworkday.com', 'myworkdayjobs.com', 'workday.com',
    'smartrecruiters.com', 'icims.com', 'jobvite.com',
    'applytojob.com', 'ashbyhq.com', 'breezy.hr',
    'recruitee.com', 'jazz.co', 'bamboohr.com',
    'taleo.net', 'successfactors.com',
}

NOREPLY_PATTERNS = [
    r'no[-_]?reply', r'noreply', r'do[-_]?not[-_]?reply',
    r'mailer[-_]?daemon', r'notifications?@',
    r'auto[-_]?reply', r'automated',
]

# Senders that should always be classified as "direct" outreach
DIRECT_OVERRIDE_SENDERS = [
    r'rexpand',
]

# ─── Noise / Non-Job Senders & Subjects ──────────────────────────────────────────
# Emails matching these are classified as "other" before job-pattern matching runs.

NOISE_SENDER_PATTERNS = [
    # LinkedIn notifications (not recruiter messages)
    r'notifications?[-@].*linkedin',
    r'messages-noreply@linkedin',
    r'invitations@linkedin',
    r'news@linkedin',
    r'editors@linkedin',
    r'digest-noreply@linkedin',
    # Social / forums
    r'@reddit\.com',
    r'@quora\.com',
    r'@discord\.com',
    r'@slack\.com',
    r'@medium\.com',
    r'@substack\.com',
    r'@stackoverflow\.com',
    r'@stackexchange\.com',
    r'@github\.com',
    r'@meetup\.com',
    r'@eventbrite\.com',
    # Marketing / newsletters
    r'@mailchimp\.com',
    r'@sendgrid\.(com|net)',
    r'@constantcontact\.com',
    r'@hubspot\.com',
    r'newsletter@',
    r'digest@',
    r'marketing@',
    r'promo(tion)?s?@',
    r'info@',
    r'updates?@',
    r'news@',
    r'announce(ment)?s?@',
    # Shopping / finance / personal services
    r'@amazon\.',
    r'@paypal\.',
    r'@venmo\.',
    r'@uber\.com',
    r'@doordash\.com',
    r'@spotify\.com',
    r'@netflix\.com',
    r'@apple\.com',
    r'@google\.(com|accounts)',
]

NOISE_SUBJECT_PATTERNS = [
    r'^your\s+daily\s+digest',
    r'^your\s+weekly\s+(digest|summary|update)',
    r'^\d+\s+new\s+(notification|connection|message|invitation|endorsement)',
    r'connection\s+request',
    r'endorsed\s+you',
    r'skill\s+endorsement',
    r'accepted\s+your\s+(invitation|connection)',
    r'is\s+now\s+a\s+connection',
    r'people\s+you\s+may\s+know',
    r'trending\s+(in|on)\s+your',
    r'newsletter',
    r'unsubscribe',
    r'subscription',
    r'^(re:\s*)?order\s+(confirm|ship|deliver)',
    r'^(re:\s*)?receipt\s+(for|from)',
    r'^(re:\s*)?payment\s+(confirm|received)',
    r'^(re:\s*)?invoice\s+#',
    r'\bverify\s+your\s+(email|account)\b',
    r'password\s+(reset|change)',
    r'two.factor|2fa|verification\s+code',
    r'sign.in\s+(attempt|alert)',
]


def _is_automated_sender(sender_email):
    """Check if the sender is an automated/no-reply address."""
    for pattern in NOREPLY_PATTERNS:
        if re.search(pattern, sender_email, re.IGNORECASE):
            return True
    return False


def classify_email(email_data):
    """
    Classify an email into a job application category.

    Returns dict with: category, confidence, company_name, job_title
    """
    subject = email_data.get('subject', '').lower()
    body = email_data.get('body_text', '').lower()
    snippet = email_data.get('snippet', '').lower()
    sender = email_data.get('sender', '').lower()
    sender_domain = email_data.get('sender_domain', '').lower()
    sender_email = email_data.get('sender_email', '').lower()

    combined_text = f"{subject} {snippet} {body}"
    is_automated = _is_automated_sender(sender_email)

    # ── Early exit: classify noise / non-job emails as "other" ──
    noise_sender = any(re.search(p, sender_email, re.IGNORECASE) for p in NOISE_SENDER_PATTERNS)
    noise_subject = any(re.search(p, subject, re.IGNORECASE) for p in NOISE_SUBJECT_PATTERNS)

    if noise_sender or noise_subject:
        return {
            'category': 'other',
            'confidence': 0.90,
            'company_name': '',
            'job_title': '',
        }

    # ── Force-classify specific senders as "direct" ──
    for pattern in DIRECT_OVERRIDE_SENDERS:
        if re.search(pattern, sender + ' ' + sender_email, re.IGNORECASE):
            company_name = _extract_company_name(email_data)
            job_title = _extract_job_title(subject, body)
            return {
                'category': 'direct',
                'confidence': 0.95,
                'company_name': company_name,
                'job_title': job_title,
            }

    # ── Subject-line priority: definitive "applied" signals in the subject
    #    always win, even if the body mentions interviews/next steps.
    SUBJECT_APPLIED_PATTERNS = [
        r'(thank\s+you|thanks)\s+for\s+(your\s+)?(applying|application|interest)',
        r'application\s+(received|confirmed|submitted)',
        r'we\s+(have\s+)?received\s+your\s+application',
        r'application\s+confirmation',
        r'you\s+(have\s+)?(successfully\s+)?applied\s+(for|to)',
        r'your\s+(application|submission)\s+has\s+been\s+(received|submitted)',
    ]
    for pattern in SUBJECT_APPLIED_PATTERNS:
        if re.search(pattern, subject, re.IGNORECASE):
            company_name = _extract_company_name(email_data)
            job_title = _extract_job_title(subject, body)
            return {
                'category': 'applied',
                'confidence': 0.98,
                'company_name': company_name,
                'job_title': job_title,
            }

    # Run all pattern matchers
    results = []

    for category, patterns in [
        ('rejection', REJECTION_PATTERNS),
        ('interview', INTERVIEW_PATTERNS),
        ('offer', OFFER_PATTERNS),
        ('follow_up', FOLLOWUP_PATTERNS),
        ('applied', APPLIED_PATTERNS),
    ]:
        best_confidence = 0.0
        for pattern, confidence in patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                best_confidence = max(best_confidence, confidence)

        if best_confidence > 0:
            results.append((category, best_confidence))

    # Sort by confidence descending
    results.sort(key=lambda x: x[1], reverse=True)

    # Determine category
    if results:
        category = results[0][0]
        confidence = results[0][1]

        # Smart override: if an automated/no-reply sender matches both
        # "interview" and "applied", it's almost certainly an application
        # confirmation, not a real interview invite.
        if is_automated and category == 'interview':
            applied_match = any(c == 'applied' for c, _ in results)
            if applied_match:
                category = 'applied'
                confidence = max(c for cat, c in results if cat == 'applied')
            else:
                # Automated emails with interview-like language that don't
                # also match applied patterns are likely confirmation emails
                # describing the hiring process, not actual invites.
                category = 'applied'
                confidence = 0.75

    elif _is_direct_company_email(sender_email, sender_domain):
        category = 'direct'
        confidence = 0.70
    else:
        category = 'other'
        confidence = 0.50

    # Extract metadata
    company_name = _extract_company_name(email_data)
    job_title = _extract_job_title(subject, body)

    return {
        'category': category,
        'confidence': confidence,
        'company_name': company_name,
        'job_title': job_title,
    }


def _is_direct_company_email(sender_email, sender_domain):
    """Check if email is directly from a company (not a job board)."""
    if not sender_domain:
        return False

    # If from a known job board, it's not a direct email
    for domain in JOB_BOARD_DOMAINS:
        if sender_domain.endswith(domain):
            return False

    # If from a noreply address, less likely to be direct
    for pattern in NOREPLY_PATTERNS:
        if re.search(pattern, sender_email, re.IGNORECASE):
            return False

    # Common email providers aren't "company" emails
    personal_domains = {'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 'icloud.com'}
    if sender_domain in personal_domains:
        return False

    return True


def _extract_company_name(email_data):
    """Try to extract the company name from the email."""
    sender = email_data.get('sender', '')
    sender_name = email_data.get('sender_name', '')
    sender_domain = email_data.get('sender_domain', '')
    subject = email_data.get('subject', '')

    # Try sender name first (often "Company via LinkedIn", "Company Careers", etc.)
    if sender_name:
        # Remove common suffixes
        name = sender_name
        for suffix in [' via LinkedIn', ' via Indeed', ' Careers', ' Recruiting',
                       ' Talent', ' Hiring', ' HR', ' Jobs', ' Team']:
            name = re.sub(re.escape(suffix), '', name, flags=re.IGNORECASE)
        name = name.strip(' "\'')
        if name and len(name) > 1 and name.lower() not in ('no reply', 'noreply', 'do not reply'):
            return name

    # Try domain-based extraction
    if sender_domain and sender_domain not in JOB_BOARD_DOMAINS:
        personal_domains = {'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com'}
        if sender_domain not in personal_domains:
            # Convert domain to company name (e.g., apple.com -> Apple)
            company = sender_domain.split('.')[0]
            return company.capitalize()

    # Try subject line patterns
    patterns = [
        r'(?:at|from|with)\s+([A-Z][A-Za-z\s&]+?)(?:\s*[-–—|]|\s+for\s+)',
        r'([A-Z][A-Za-z\s&]+?)\s+(?:is|has|would)',
    ]
    for pattern in patterns:
        match = re.search(pattern, subject)
        if match:
            return match.group(1).strip()

    return ''


def _extract_job_title(subject, body):
    """Try to extract job title from email content."""
    text = f"{subject} {body[:1000]}"

    patterns = [
        r'(?:position|role|job|opening)\s*(?:of|for|:)\s*(.+?)(?:\.|,|\n|$)',
        r'(?:applied\s+(?:for|to)\s+(?:the\s+)?)([\w\s]+?)(?:\s+(?:position|role|at|with)|\.|,|\n|$)',
        r'(?:application\s+for\s+(?:the\s+)?)([\w\s]+?)(?:\s+(?:position|role|at|with)|\.|,|\n|$)',
        r'(?:interview\s+for\s+(?:the\s+)?)([\w\s]+?)(?:\s+(?:position|role|at|with)|\.|,|\n|$)',
        r're:\s*(.+?)(?:\s+(?:at|with|-|–)\s+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Clean up
            title = re.sub(r'\s+', ' ', title)
            if 3 < len(title) < 80:
                return title

    return ''


def classify_emails(emails):
    """Classify a list of emails. Returns emails with classification data merged in."""
    classified = []
    for email in emails:
        classification = classify_email(email)
        email.update(classification)
        classified.append(email)
    return classified
