"""
Parser for PDF (.pdf) resume documents
"""

from pathlib import Path
from typing import Dict, Any, List

from career_forge.parsers.base import BaseParser, ParsedDocument, segment_text_sections
from career_forge.core.exceptions import ParserError


class PdfParser(BaseParser):
    """Parses PDF documents using pypdf or graceful fallback."""

    def parse_file(self, file_path: Path) -> ParsedDocument:
        path = Path(file_path)
        if not path.exists():
            raise ParserError(f"File not found: {path}")

        MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB threshold
        if path.stat().st_size > MAX_FILE_SIZE:
            raise ParserError(f"Security: PDF file size ({path.stat().st_size} bytes) exceeds 25MB limit.")

        try:
            import pypdf
            reader = pypdf.PdfReader(str(path))
            pages_text = []
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    pages_text.append(text)
            
            full_text = "\n\n".join(pages_text).strip()
            sections = segment_text_sections(full_text)
            return ParsedDocument(
                raw_text=full_text,
                clean_text=full_text,
                file_type="pdf",
                file_path=str(path),
                metadata={"page_count": len(reader.pages)},
                sections=sections
            )
        except ImportError:
            # Fallback if pypdf is not installed
            raise ParserError("pypdf is required to parse PDF documents. Install via `pip install pypdf`.")
        except Exception as e:
            raise ParserError(f"Failed to parse PDF document {path}: {e}") from e

    def parse_text(self, text: str) -> ParsedDocument:
        raise NotImplementedError("PDF parser requires binary/file input.")
