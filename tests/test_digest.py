"""
Unit tests for ProfileDigestEngine (150-token structured digest & token optimization)
"""

import unittest
from pathlib import Path

from career_forge.parsers import parse_resume_file
from career_forge.engines.digest import ProfileDigestEngine

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "synthetic_resumes"


class TestDigest(unittest.TestCase):
    def setUp(self):
        self.engine = ProfileDigestEngine()

    def test_digest_from_backend_md(self):
        doc = parse_resume_file(FIXTURES_DIR / "alex_rivera_backend.md")
        digest = self.engine.extract_digest(doc)

        self.assertEqual(digest.candidate_name, "Alex Rivera")
        self.assertIn("Go", digest.core_stack)
        self.assertIn("Kafka", digest.core_stack)
        self.assertIn("Kubernetes", digest.core_stack)
        self.assertTrue(any("45,000" in m or "35%" in m for m in digest.top_metrics))
        self.assertIn("SENIOR", digest.career_stage.upper())
        
        # Verify compact JSON representation
        json_str = digest.to_json()
        self.assertTrue(len(json_str) < 1200)  # ~150-250 tokens

    def test_digest_from_sdet_txt(self):
        doc = parse_resume_file(FIXTURES_DIR / "jordan_taylor_sdet.txt")
        digest = self.engine.extract_digest(doc)

        self.assertEqual(digest.candidate_name, "Jordan Taylor")
        self.assertIn("Playwright", digest.core_stack)
        self.assertIn("Python", digest.core_stack)
        self.assertTrue(any("70%" in m or "140+" in m for m in digest.top_metrics))

    def test_digest_from_aiml_tex(self):
        doc = parse_resume_file(FIXTURES_DIR / "morgan_chen_aiml.tex")
        digest = self.engine.extract_digest(doc)

        self.assertEqual(digest.candidate_name, "Morgan Chen")
        self.assertIn("PyTorch", digest.core_stack)
        self.assertIn("vLLM", digest.core_stack)
        self.assertTrue(any("3.2x" in m or "91%" in m for m in digest.top_metrics))


if __name__ == "__main__":
    unittest.main()
