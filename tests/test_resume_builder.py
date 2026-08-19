"""
Unit tests for ResumeArchitectEngine (100-Point ATS Audit & LaTeX Generation)
"""

import unittest
from pathlib import Path

from career_forge.parsers import parse_resume_file
from career_forge.engines.resume_builder import ResumeArchitectEngine, AtsAuditReport

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "synthetic_resumes"


class TestResumeBuilder(unittest.TestCase):
    def setUp(self):
        self.engine = ResumeArchitectEngine()

    def test_100_point_ats_audit(self):
        doc = parse_resume_file(FIXTURES_DIR / "alex_rivera_backend.md")
        audit = self.engine.audit_ats_score(doc)

        self.assertIsInstance(audit, AtsAuditReport)
        self.assertGreaterEqual(audit.total_score, 80)
        self.assertGreaterEqual(audit.action_verb_score, 18)
        self.assertGreaterEqual(audit.metric_density_score, 18)
        self.assertGreaterEqual(audit.structure_score, 20)

    def test_latex_resume_generation(self):
        doc = parse_resume_file(FIXTURES_DIR / "alex_rivera_backend.md")
        tex_code = self.engine.generate_latex(doc, role_template="swe")

        self.assertIn(r"\documentclass", tex_code)
        self.assertIn("Alex Rivera", tex_code)
        self.assertIn("Nexus Cloud Systems", tex_code)
        self.assertIn(r"\begin{itemize}", tex_code)

    def test_bidirectional_conversion(self):
        doc = parse_resume_file(FIXTURES_DIR / "morgan_chen_aiml.tex")
        md_text = self.engine.convert_format(doc, target_format="md")
        self.assertIn("# Morgan Chen", md_text)
        self.assertIn("Applied AI & LLM Systems Engineer", md_text)


if __name__ == "__main__":
    unittest.main()
