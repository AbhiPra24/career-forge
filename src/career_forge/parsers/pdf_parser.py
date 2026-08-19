"""
Parser for PDF (.pdf) resume documents
"""

from pathlib import Path
from typing import Dict, Any, List

from career_forge.parsers.base import BaseParser, ParsedDocument
from career_forge.core.exceptions import ParserError


class PdfParser(BaseParser):
    """Parses PDF documents using pypdf or graceful fallback."""

    def parse_file(self, file_path: Path) -> ParsedDocument:
        path = Path(file_path)
        if not path.exists():
            raise ParserError(f"File not found: {path}")

        try:
            import pypdf
            reader = pypdf.PdfReader(str(path))
            pages_text = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages_text.append(text)
            
            full_text = "\n\n".join(pages_text).strip()
            return ParsedDocument(
                raw_text=full_text,
                clean_text=full_text,
                file_type="pdf",
                file_path=str(path),
                metadata={"page_count": len(reader.pages)}
            )
        except ImportError:
            # Fallback if pypdf is not installed
            raise ParserError("pypdf is required to parse PDF documents. Install via `pip install pypdf`.")
        except Exception as e:
            raise ParserError(f"Failed to parse PDF document {path}: {e}") from e

    def parse_text(self, text: str) -> ParsedDocument:
        raise NotImplementedError("PDF parser requires binary/file input.")
