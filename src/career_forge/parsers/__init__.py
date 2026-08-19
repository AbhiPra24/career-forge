"""
Parsers module with auto-detecting factory
"""

from pathlib import Path
from career_forge.parsers.base import BaseParser, ParsedDocument
from career_forge.parsers.text_parser import TextParser
from career_forge.parsers.docx_parser import DocxParser
from career_forge.parsers.latex_parser import LatexParser
from career_forge.parsers.pdf_parser import PdfParser
from career_forge.core.exceptions import ParserError


def get_parser_for_file(file_path: Path) -> BaseParser:
    """Returns the appropriate BaseParser instance based on file extension."""
    path = Path(file_path)
    ext = path.suffix.lower()
    
    if ext in (".md", ".txt", ".json"):
        return TextParser()
    elif ext in (".tex", ".latex"):
        return LatexParser()
    elif ext in (".docx",):
        return DocxParser()
    elif ext in (".pdf",):
        return PdfParser()
    else:
        # Default to TextParser for arbitrary extensions
        return TextParser()


def parse_resume_file(file_path: Path) -> ParsedDocument:
    """Convenience helper to auto-detect and parse any supported resume file."""
    parser = get_parser_for_file(file_path)
    return parser.parse_file(file_path)


__all__ = [
    "BaseParser",
    "ParsedDocument",
    "TextParser",
    "DocxParser",
    "LatexParser",
    "PdfParser",
    "get_parser_for_file",
    "parse_resume_file",
]
