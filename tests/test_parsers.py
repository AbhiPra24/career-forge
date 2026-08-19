"""
Unit tests for CareerForge Multi-Format Document Parsers
"""

import unittest
from pathlib import Path

from career_forge.parsers import (
    TextParser,
    LatexParser,
    DocxParser,
    get_parser_for_file,
    parse_resume_file,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "synthetic_resumes"


class TestParsers(unittest.TestCase):
    def test_markdown_parser(self):
        md_file = FIXTURES_DIR / "alex_rivera_backend.md"
        doc = parse_resume_file(md_file)
        self.assertEqual(doc.file_type, "md")
        self.assertIn("Alex Rivera", doc.clean_text)
        self.assertIn("Distributed Systems", doc.clean_text)
        self.assertIn("Nexus Cloud Systems", doc.clean_text)

    def test_json_parser(self):
        json_file = FIXTURES_DIR / "alex_rivera_backend.json"
        doc = parse_resume_file(json_file)
        self.assertEqual(doc.file_type, "json")
        self.assertEqual(doc.metadata.get("name"), "Alex Rivera")
        self.assertIn("Kafka", doc.clean_text)

    def test_plain_text_parser(self):
        txt_file = FIXTURES_DIR / "jordan_taylor_sdet.txt"
        doc = parse_resume_file(txt_file)
        self.assertEqual(doc.file_type, "txt")
        self.assertIn("JORDAN TAYLOR", doc.clean_text)
        self.assertIn("Playwright", doc.clean_text)

    def test_latex_parser(self):
        tex_file = FIXTURES_DIR / "morgan_chen_aiml.tex"
        doc = parse_resume_file(tex_file)
        self.assertEqual(doc.file_type, "tex")
        self.assertIn("Morgan Chen", doc.clean_text)
        self.assertIn("Applied AI & LLM Systems Engineer", doc.clean_text)
        self.assertIn("PyTorch", doc.clean_text)
        # Verify LaTeX markup stripped
        self.assertNotIn(r"\documentclass", doc.clean_text)
        self.assertNotIn(r"\begin{itemize}", doc.clean_text)


if __name__ == "__main__":
    unittest.main()
