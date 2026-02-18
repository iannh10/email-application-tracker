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
