"""
Unit tests for TalentScoutEngine (4-Factor Matcher & Requisition Discovery)
"""

import unittest
from pathlib import Path

from career_forge.parsers import parse_resume_file
from career_forge.engines.digest import ProfileDigestEngine
from career_forge.engines.matcher import TalentScoutEngine, JobListing, EvaluationResult
from career_forge.engines.discovery import DiscoveryEngine

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "synthetic_resumes"


class TestMatcher(unittest.TestCase):
    def setUp(self):
        self.digest_engine = ProfileDigestEngine()
        self.matcher = TalentScoutEngine()
        self.discovery = DiscoveryEngine()

    def test_4_factor_fit_scoring(self):
        doc = parse_resume_file(FIXTURES_DIR / "alex_rivera_backend.md")
        digest = self.digest_engine.extract_digest(doc)

        job = JobListing(
            title="Senior Distributed Systems Engineer",
            company="Nexus Stream Inc",
            location="Remote",
            tier="Tier 1 (Product Unicorn)",
            requirements=["Go", "Kafka", "Kubernetes", "gRPC", "PostgreSQL"],
            description="Looking for a Senior Go Engineer with Kafka and Kubernetes experience to scale streaming systems."
        )

        eval_res = self.matcher.evaluate_fit(digest, job)

        self.assertIsInstance(eval_res, EvaluationResult)
        self.assertGreaterEqual(eval_res.fit_score, 80.0)
        self.assertEqual(eval_res.action_batch, "Batch 1 (Immediate Apply)")
        self.assertIn("Go", eval_res.matched_skills)
        self.assertIn("Kafka", eval_res.matched_skills)

    def test_low_fit_classification(self):
        doc = parse_resume_file(FIXTURES_DIR / "alex_rivera_backend.md")
        digest = self.digest_engine.extract_digest(doc)

        job = JobListing(
            title="Senior iOS Mobile Developer",
            company="AppCrafters",
            location="San Francisco, CA",
            tier="Tier 3 (Startup)",
            requirements=["Swift", "SwiftUI", "CoreData", "Combine", "XCode"],
            description="Senior iOS Developer building high quality mobile interfaces."
        )

        eval_res = self.matcher.evaluate_fit(digest, job)
        self.assertLess(eval_res.fit_score, 65.0)
        self.assertEqual(eval_res.action_batch, "Batch 3 (Safety Net / Alternate)")

    def test_discovery_and_report_generation(self):
        doc = parse_resume_file(FIXTURES_DIR / "alex_rivera_backend.md")
        digest = self.digest_engine.extract_digest(doc)

        jobs = self.discovery.discover_jobs(query="Distributed Systems", location="Remote", limit=10)
        self.assertGreaterEqual(len(jobs), 10)

        report_md = self.discovery.generate_strategy_report(digest, jobs, self.matcher)
        self.assertIn("Alex Rivera", report_md)
        self.assertIn("JOB RESEARCH STRATEGY REPORT", report_md)
        self.assertIn("Top Open Requisitions", report_md)


if __name__ == "__main__":
    unittest.main()
