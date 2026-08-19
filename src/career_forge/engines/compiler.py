"""
Deterministic LaTeX Compiler Bridge with Graceful Fallback
Hierarchy: Tectonic -> XeLaTeX -> pdfLaTeX -> Graceful degradation
"""

import shutil
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from career_forge.core.exceptions import CompilationError


@dataclass
class CompilationResult:
    """Result of LaTeX compilation attempt."""
    success: bool
    tex_path: Path
    pdf_path: Optional[Path] = None
    engine_used: Optional[str] = None
    warning: Optional[str] = None
    stdout: str = ""
    stderr: str = ""


class CompilerBridge:
    """Discovers available LaTeX binaries and compiles .tex to ATS-optimized .pdf."""

    def __init__(self):
        self.preferred_engine = self.detect_compiler()

    def detect_compiler(self) -> Optional[str]:
        """Detects compiler engine following priority: tectonic -> xelatex -> pdflatex."""
        if shutil.which("tectonic"):
            return "tectonic"
        elif shutil.which("xelatex"):
            return "xelatex"
        elif shutil.which("pdflatex"):
            return "pdflatex"
        return None

    def compile_latex_to_pdf(self, tex_file: Path, output_dir: Optional[Path] = None) -> CompilationResult:
        """
        Compiles .tex to .pdf. If no compiler is available, preserves the .tex file
        and returns a friendly warning without raising an unhandled exception.
        """
        tex_path = Path(tex_file).resolve()
        if not tex_path.exists():
            raise CompilationError(f"LaTeX file not found: {tex_path}")

        out_dir = Path(output_dir or tex_path.parent).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = out_dir / f"{tex_path.stem}.pdf"

        engine = self.detect_compiler()
        if not engine:
            return CompilationResult(
                success=False,
                tex_path=tex_path,
                pdf_path=None,
                engine_used=None,
                warning=(
                    "No LaTeX compiler found on system (checked: tectonic, xelatex, pdflatex).\n"
                    "Preserved pristine .tex file. To compile to PDF, install tectonic:\n"
                    "  • macOS: brew install tectonic\n"
                    "  • Linux: apt-get install tectonic  OR  cargo install tectonic"
                )
            )

        try:
            if engine == "tectonic":
                cmd = ["tectonic", "--outdir", str(out_dir), str(tex_path)]
            elif engine == "xelatex":
                cmd = ["xelatex", "-interaction=nonstopmode", f"-output-directory={out_dir}", str(tex_path)]
            else:  # pdflatex
                cmd = ["pdflatex", "-interaction=nonstopmode", f"-output-directory={out_dir}", str(tex_path)]

            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(tex_path.parent),
                timeout=30
            )

            if proc.returncode == 0 and pdf_path.exists():
                return CompilationResult(
                    success=True,
                    tex_path=tex_path,
                    pdf_path=pdf_path,
                    engine_used=engine,
                    stdout=proc.stdout,
                    stderr=proc.stderr
                )
            else:
                return CompilationResult(
                    success=False,
                    tex_path=tex_path,
                    pdf_path=None,
                    engine_used=engine,
                    warning=f"Compilation with {engine} exited with code {proc.returncode}.",
                    stdout=proc.stdout,
                    stderr=proc.stderr
                )
        except Exception as e:
            return CompilationResult(
                success=False,
                tex_path=tex_path,
                pdf_path=None,
                engine_used=engine,
                warning=f"LaTeX compilation failed: {e}"
            )
