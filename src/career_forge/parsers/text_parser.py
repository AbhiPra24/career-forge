"""
Parser for Plain Text, Markdown, and JSON documents
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

from career_forge.parsers.base import BaseParser, ParsedDocument
from career_forge.core.exceptions import ParserError


class TextParser(BaseParser):
    """Parses .txt, .md, and .json files into clean text and structured sections."""

    def parse_file(self, file_path: Path) -> ParsedDocument:
        path = Path(file_path)
        if not path.exists():
            raise ParserError(f"File not found: {path}")
        
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            doc = self.parse_text(content)
            doc.file_path = str(path)
            doc.file_type = path.suffix.lstrip(".").lower() or "txt"
            return doc
        except Exception as e:
            raise ParserError(f"Failed to parse text document {path}: {e}") from e

    def parse_text(self, text: str) -> ParsedDocument:
        clean = text.strip()
        metadata: Dict[str, Any] = {}
        sections: Dict[str, str] = {}

        # Check if JSON
        if clean.startswith("{") and clean.endswith("}"):
            try:
                data = json.loads(clean)
                metadata = data
                clean = json.dumps(data, indent=2)
                return ParsedDocument(
                    raw_text=text,
                    clean_text=clean,
                    file_type="json",
                    metadata=metadata,
                    sections={"json_root": clean}
                )
            except json.JSONDecodeError:
                pass

        # Extract Markdown/Text Sections
        lines = clean.splitlines()
        current_section = "Header"
        section_lines = []

        for line in lines:
            header_match = re.match(r"^(?:#{1,4}\s+|[A-Z\s]{4,}:?$)(.+)$", line.strip())
            if header_match and len(line.strip()) < 60:
                if section_lines:
                    sections[current_section] = "\n".join(section_lines).strip()
                    section_lines = []
                current_section = header_match.group(1).strip("#: ")
            else:
                section_lines.append(line)

        if section_lines:
            sections[current_section] = "\n".join(section_lines).strip()

        return ParsedDocument(
            raw_text=text,
            clean_text=clean,
            file_type="text",
            metadata=metadata,
            sections=sections
        )
