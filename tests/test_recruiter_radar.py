"""
Unit tests for RecruiterRadarEngine (Email Deliverability & MX Verification)
"""

import unittest
from career_forge.engines.recruiter_radar import RecruiterRadarEngine, DeliverabilityStatus


class TestRecruiterRadar(unittest.TestCase):
    def setUp(self):
        self.radar = RecruiterRadarEngine()

    def test_rfc5322_validation(self):
        self.assertTrue(self.radar.validate_email_syntax("sarah.connor@datadoghq.com"))
        self.assertTrue(self.radar.validate_email_syntax("recruiter+tech@stripe.com"))
        self.assertFalse(self.radar.validate_email_syntax("invalid-email-address"))
        self.assertFalse(self.radar.validate_email_syntax("@no-user.com"))

    def test_generic_alias_detection(self):
        self.assertTrue(self.radar.is_generic_alias("recruiting@company.com"))
        self.assertTrue(self.radar.is_generic_alias("careers@company.com"))
        self.assertTrue(self.radar.is_generic_alias("jobs@company.com"))
        self.assertTrue(self.radar.is_generic_alias("hr@company.com"))
        self.assertFalse(self.radar.is_generic_alias("alex.recruiter@company.com"))

    def test_deliverability_evaluation(self):
        # Valid named recruiter on real domain
        status = self.radar.verify_email("talent.lead@github.com")
        self.assertIsInstance(status, DeliverabilityStatus)
        self.assertTrue(status.is_valid_syntax)
        self.assertFalse(status.is_generic_alias)
        
        # Generic unmonitored alias
        alias_status = self.radar.verify_email("careers@stripe.com")
        self.assertTrue(alias_status.is_generic_alias)
        self.assertIn("BOUNCE", alias_status.confidence)

    def test_outreach_templates_generation(self):
        templates = self.radar.generate_outreach_templates(
            candidate_name="Alex Rivera",
            role_title="Senior Backend Engineer",
            target_company="Nexus",
            top_metric="Scaled Kafka streaming to 45k RPS"
        )
        self.assertIn("hiring_manager", templates)
        self.assertIn("recruiter", templates)
        self.assertIn("peer_referral", templates)
        self.assertIn("Alex Rivera", templates["hiring_manager"])


if __name__ == "__main__":
    unittest.main()
