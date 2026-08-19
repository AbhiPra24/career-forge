"""
Unit tests for CompilerBridge (Deterministic Binary Discovery & Fallback)
"""

import unittest
import tempfile
from pathlib import Path

from career_forge.engines.compiler import CompilerBridge, CompilationResult


class TestCompiler(unittest.TestCase):
    def setUp(self):
        self.compiler = CompilerBridge()

    def test_compiler_discovery(self):
        engine = self.compiler.detect_compiler()
        # Returns string engine or None
        self.assertIn(engine, ("tectonic", "xelatex", "pdflatex", None))

    def test_compile_graceful_fallback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_file = Path(tmpdir) / "test_resume.tex"
            tex_file.write_text(r"""
\documentclass{article}
\begin{document}
Test Resume
\end{document}
            """)

            res = self.compiler.compile_latex_to_pdf(tex_file, output_dir=Path(tmpdir))
            self.assertIsInstance(res, CompilationResult)
            if res.success:
                self.assertTrue(res.pdf_path.exists())
            else:
                self.assertIsNotNone(res.warning)
                self.assertIn("install", res.warning.lower())


if __name__ == "__main__":
    unittest.main()
