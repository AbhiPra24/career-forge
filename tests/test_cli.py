"""
Unit tests for CareerForge CLI Commands (`cforge`)
"""

import sys
import unittest
import tempfile
from pathlib import Path
from io import StringIO
from unittest.mock import patch

from career_forge.cli import main

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "synthetic_resumes"


class TestCLI(unittest.TestCase):
    def test_cli_help(self):
        with patch("sys.argv", ["cforge", "--help"]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)

    def test_cli_resume_audit(self):
        resume = str(FIXTURES_DIR / "alex_rivera_backend.md")
        with patch("sys.argv", ["cforge", "resume", "audit", "--resume", resume]):
            main()

    def test_cli_resume_audit_json(self):
        resume = str(FIXTURES_DIR / "alex_rivera_backend.md")
        with patch("sys.argv", ["cforge", "resume", "audit", "--resume", resume, "--json"]):
            main()

    def test_cli_resume_convert(self):
        resume = str(FIXTURES_DIR / "morgan_chen_aiml.tex")
        with tempfile.TemporaryDirectory() as tmpdir:
            out_md = Path(tmpdir) / "converted.md"
            with patch("sys.argv", ["cforge", "resume", "convert", "--input", resume, "--to", "md", "--output", str(out_md)]):
                main()
                self.assertTrue(out_md.exists())

    def test_cli_resume_build(self):
        resume = str(FIXTURES_DIR / "alex_rivera_backend.md")
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("sys.argv", ["cforge", "resume", "build", "--resume", resume, "--role", "swe", "--output", tmpdir]):
                main()
                # Verify .tex created
                tex_files = list(Path(tmpdir).glob("*.tex"))
                self.assertTrue(len(tex_files) > 0)

    def test_cli_match(self):
        resume = str(FIXTURES_DIR / "alex_rivera_backend.md")
        with patch("sys.argv", ["cforge", "match", "--resume", resume, "--limit", "5"]):
            main()

    def test_cli_match_json(self):
        resume = str(FIXTURES_DIR / "alex_rivera_backend.md")
        with patch("sys.argv", ["cforge", "match", "--resume", resume, "--limit", "5", "--json"]):
            main()

    def test_cli_verify_email(self):
        with patch("sys.argv", ["cforge", "verify-email", "recruiter@github.com"]):
            main()

    def test_cli_verify_email_json(self):
        with patch("sys.argv", ["cforge", "verify-email", "recruiter@github.com", "--json"]):
            main()


if __name__ == "__main__":
    unittest.main()
