"""
Parser for LaTeX (.tex) resume documents
"""

import re
from pathlib import Path
from typing import Dict, Any, List

from career_forge.parsers.base import BaseParser, ParsedDocument
from career_forge.core.exceptions import ParserError


class LatexParser(BaseParser):
    """Parses LaTeX source files, extracts plain text and tokenized sections."""

    def parse_file(self, file_path: Path) -> ParsedDocument:
        path = Path(file_path)
        if not path.exists():
            raise ParserError(f"File not found: {path}")

        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            doc = self.parse_text(content)
            doc.file_path = str(path)
            doc.file_type = "tex"
            return doc
        except Exception as e:
            raise ParserError(f"Failed to parse LaTeX file {path}: {e}") from e

    def parse_text(self, text: str) -> ParsedDocument:
        # 1. Strip comments (ignore escaped \%)
        lines = [re.split(r"(?<!\\)%", line)[0] for line in text.splitlines()]
        code = "\n".join(lines)

        # 2. Extract sections
        sections: Dict[str, str] = {}
        section_pattern = re.compile(r"\\section\*?\{([^}]+)\}([\s\S]*?)(?=\\section\*?\{|\Z)", re.MULTILINE)
        for match in section_pattern.finditer(code):
            title = match.group(1).strip()
            body = self._clean_latex_syntax(match.group(2).strip())
            sections[title] = body

        # 3. Clean full text
        clean = self._clean_latex_syntax(code)

        return ParsedDocument(
            raw_text=text,
            clean_text=clean,
            file_type="tex",
            sections=sections
        )

    def _clean_latex_syntax(self, raw: str) -> str:
        s = raw
        # Remove documentclass, usepackage, geometry, begin/end document/itemize/center
        s = re.sub(r"\\documentclass.*?\{.*?\}", "", s)
        s = re.sub(r"\\usepackage.*?\{.*?\}", "", s)
        s = re.sub(r"\\geometry\{.*?\}", "", s)
        s = re.sub(r"\\(begin|end)\{[a-zA-Z*]+\}", "", s)
        # Convert commands
        s = re.sub(r"\\textbf\{([^}]+)\}", r"\1", s)
        s = re.sub(r"\\textit\{([^}]+)\}", r"\1", s)
        s = re.sub(r"\\LARGE", "", s)
        s = re.sub(r"\\vspace\{.*?\}", "", s)
        s = re.sub(r"\\hfill", " | ", s)
        s = re.sub(r"\\item\s+", "• ", s)
        s = re.sub(r"\\\\", "\n", s)
        s = s.replace(r"\textbar", "|").replace(r"--", "–")
        s = s.replace(r"\%", "%").replace(r"\&", "&").replace(r"\$", "$").replace(r"\_", "_").replace(r"\#", "#")
        s = re.sub(r"\\[a-zA-Z]+\*?", "", s)
        # Clean extra braces, backslashes and whitespace
        s = re.sub(r"[{}]", "", s)
        s = s.replace("\\", "")
        s = re.sub(r"\n{3,}", "\n\n", s)
        return s.strip()
