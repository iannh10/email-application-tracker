"""
Test suite for the email classifier — focused on interview invite detection
for HireVue, online assessments, and coding challenges.
"""
import pytest
from email_classifier import classify_email


def _make_email(subject, body, sender_email="recruiter@company.com", sender="Company Recruiting"):
    """Helper to construct a minimal email dict."""
    return {
        "subject": subject,
        "body_text": body,
        "snippet": body[:100],
        "sender": sender,
        "sender_email": sender_email,
        "sender_name": sender.split("<")[0].strip(),
        "sender_domain": sender_email.split("@")[-1] if "@" in sender_email else "",
    }


# ────────────────────────────────────────────────────────────────────────────
# Tier 1: Explicit HireVue / assessment invitations
# ────────────────────────────────────────────────────────────────────────────

class TestTier1HireVue:
    def test_complete_your_hirevue(self):
        email = _make_email(
            "Next Steps: Complete your HireVue",
            "Hi, please complete your HireVue video interview at your earliest convenience."
        )
        result = classify_email(email)
        assert result["category"] == "interview", f"Expected interview, got {result['category']}"

    def test_take_the_hirevue(self):
        email = _make_email(
            "Action Required",
            "We'd like you to take the HireVue assessment as part of the next round."
        )
        result = classify_email(email)
        assert result["category"] == "interview"

    def test_invited_to_complete_online_assessment(self):
        email = _make_email(
            "Online Assessment Invitation",
            "You have been invited to complete an online assessment for the Software Engineer role."
        )
        result = classify_email(email)
        assert result["category"] == "interview"

    def test_invited_to_take_virtual_evaluation(self):
        email = _make_email(
            "Virtual Evaluation",
            "You are invited to take a virtual evaluation as part of our hiring process."
        )
        result = classify_email(email)
        assert result["category"] == "interview"

    def test_like_you_to_complete_assessment(self):
        email = _make_email(
            "Next Steps",
            "We'd like you to complete an assessment as part of our interview process."
        )
        result = classify_email(email)
        assert result["category"] == "interview"

    def test_selected_for_coding_challenge(self):
        email = _make_email(
            "Coding Challenge",
            "You have been selected for a coding challenge. Please complete it within 7 days."
        )
        result = classify_email(email)
        assert result["category"] == "interview"

    def test_next_step_complete_hirevue(self):
        email = _make_email(
            "Your Application Update",
            "As a next step, please complete the HireVue interview."
        )
        result = classify_email(email)
        assert result["category"] == "interview"


# ────────────────────────────────────────────────────────────────────────────
# Tier 2: Subject keyword + action signal
# ────────────────────────────────────────────────────────────────────────────

class TestTier2SubjectAndAction:
    def test_hirevue_in_subject_with_action(self):
        email = _make_email(
            "HireVue Interview - Software Engineer",
            "Please click the link below to access your HireVue interview."
        )
        result = classify_email(email)
        assert result["category"] == "interview"

    def test_online_assessment_in_subject_with_action(self):
        email = _make_email(
            "Online Assessment for Data Analyst",
            "Please complete the assessment by Friday. Click the link to begin."
        )
        result = classify_email(email)
        assert result["category"] == "interview"

    def test_hackerrank_in_subject_with_action(self):
        email = _make_email(
            "HackerRank Challenge",
            "Please click the link to start your coding challenge. Deadline to complete is 3 days."
        )
        result = classify_email(email)
        assert result["category"] == "interview"

    def test_pymetrics_in_subject_with_action(self):
        email = _make_email(
            "Pymetrics Assessment - Next Steps",
            "Please complete your Pymetrics games. Use the link below to get started."
        )
        result = classify_email(email)
        assert result["category"] == "interview"

    def test_skill_assessment_in_subject_with_action(self):
        email = _make_email(
            "Skills Assessment Invitation",
            "Please confirm your availability and access the assessment portal."
        )
        result = classify_email(email)
        assert result["category"] == "interview"

    def test_assessment_invite_in_subject_with_action(self):
        email = _make_email(
            "Assessment Invitation",
            "Click the link below to begin your assessment. Deadline to complete is 48 hours."
        )
        result = classify_email(email)
        assert result["category"] == "interview"


# ────────────────────────────────────────────────────────────────────────────
# Negative / guard tests — things that should NOT be classified as interview
# ────────────────────────────────────────────────────────────────────────────

class TestNegativeCases:
    def test_application_confirmation_mentioning_assessment(self):
        """Automated application-confirmation email that mentions assessment in boilerplate."""
        email = _make_email(
            "Thank you for your application",
            "We have received your application. Our process may include an online assessment and interviews.",
            sender_email="noreply@company.com",
            sender="Company Careers",
        )
        result = classify_email(email)
        assert result["category"] == "applied", f"Expected applied, got {result['category']}"

    def test_rejection_mentioning_assessment(self):
        email = _make_email(
            "Update on your application",
            "After careful consideration, we will not be moving forward with your candidacy. "
            "We appreciate you completing the assessment."
        )
        result = classify_email(email)
        assert result["category"] == "rejection"

    def test_generic_email_mentioning_assessment(self):
        """An email with 'assessment' but no action signal and not in subject → not interview."""
        email = _make_email(
            "Company Newsletter",
            "We have revamped our assessment process to be more candidate-friendly.",
            sender_email="newsletter@randomcorp.com",
            sender="RandomCorp News",
        )
        result = classify_email(email)
        # Should be 'other' due to noise sender pattern
        assert result["category"] == "other"


# ────────────────────────────────────────────────────────────────────────────
# Legacy interview tests — existing patterns should still work
# ────────────────────────────────────────────────────────────────────────────

class TestLegacyInterviewPatterns:
    def test_invite_to_phone_interview(self):
        email = _make_email(
            "Interview Invitation",
            "We'd like to invite you to a phone interview for the PM role."
        )
        result = classify_email(email)
        assert result["category"] == "interview"

    def test_interview_scheduled(self):
        email = _make_email(
            "Interview Confirmation",
            "Your interview has been scheduled for next Tuesday at 2 PM."
        )
        result = classify_email(email)
        assert result["category"] == "interview"

    def test_schedule_your_interview(self):
        email = _make_email(
            "Next Steps",
            "We'd like to schedule an interview with you. Please select a time."
        )
        result = classify_email(email)
        assert result["category"] == "interview"


# ────────────────────────────────────────────────────────────────────────────
# Direct outreach — recruiter / company reaching out proactively
# ────────────────────────────────────────────────────────────────────────────

class TestDirectOutreach:
    """Positive cases: genuine recruiter outreach → should be 'direct'."""

    def test_came_across_your_profile(self):
        email = _make_email(
            "Opportunity at Acme Corp",
            "Hi, I came across your profile on LinkedIn and think you'd be a great fit."
        )
        result = classify_email(email)
        assert result["category"] == "direct", f"Expected direct, got {result['category']}"

    def test_reaching_out_about_opportunity(self):
        email = _make_email(
            "Software Engineer Role",
            "I'm reaching out about an opportunity at our company. Would love to chat."
        )
        result = classify_email(email)
        assert result["category"] == "direct"

    def test_recruiter_intro(self):
        email = _make_email(
            "Exciting Role",
            "I am a recruiter at Acme Corp. We have a position that matches your background.",
            sender_email="jane@acmecorp.com",
            sender="Jane Smith",
        )
        result = classify_email(email)
        assert result["category"] == "direct"

    def test_would_you_be_interested(self):
        email = _make_email(
            "New Opportunity",
            "Would you be interested in discussing a Senior Engineer role at our company?"
        )
        result = classify_email(email)
        assert result["category"] == "direct"

    def test_great_fit_for_role(self):
        email = _make_email(
            "Role at StartupXYZ",
            "I think you would be a great fit for our open Backend Engineer position."
        )
        result = classify_email(email)
        assert result["category"] == "direct"

    def test_talent_acquisition_from(self):
        email = _make_email(
            "Career Opportunity",
            "I'm a talent acquisition specialist from Meta. Found your profile on LinkedIn.",
            sender_email="recruiter@meta.com",
            sender="Meta Recruiting",
        )
        result = classify_email(email)
        assert result["category"] == "direct"

    def test_override_sender_rexpand(self):
        """Senders in DIRECT_OVERRIDE_SENDERS always classify as 'direct'."""
        email = _make_email(
            "Some subject",
            "Some generic body text.",
            sender_email="team@rexpand.com",
            sender="Rexpand",
        )
        result = classify_email(email)
        assert result["category"] == "direct"


class TestDirectNegativeCases:
    """Negative: generic company emails should NOT be classified as 'direct'."""

    def test_generic_company_email_not_direct(self):
        """A plain email from a company domain without outreach language → 'other'."""
        email = _make_email(
            "Company Update",
            "Here is our quarterly earnings report.",
            sender_email="ir@somecorp.com",
            sender="SomeCorp Investor Relations",
        )
        result = classify_email(email)
        assert result["category"] != "direct", f"Should not be direct, got {result['category']}"

    def test_automated_company_email_not_direct(self):
        """Automated company email without outreach language → not 'direct'."""
        email = _make_email(
            "Welcome to our platform",
            "Thanks for signing up. Here's how to get started.",
            sender_email="noreply@techcorp.com",
            sender="TechCorp",
        )
        result = classify_email(email)
        assert result["category"] != "direct"

    def test_job_board_email_not_direct(self):
        """Email from a job board domain → not 'direct'."""
        email = _make_email(
            "New jobs for you",
            "Here are 5 new jobs matching your search.",
            sender_email="noreply@indeed.com",
            sender="Indeed",
        )
        result = classify_email(email)
        assert result["category"] != "direct"
