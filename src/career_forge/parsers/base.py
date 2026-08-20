"""
Abstract Base Parser definition and common data structures
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


import re


@dataclass
class ParsedDocument:
    """Standardized parsed document representation."""
    raw_text: str
    clean_text: str
    file_type: str
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    sections: Dict[str, str] = field(default_factory=dict)
    tables: List[List[List[str]]] = field(default_factory=list)


def segment_text_sections(text: str) -> Dict[str, str]:
    """Extracts standard resume sections from freeform or markdown text."""
    lines = text.splitlines()
    sections: Dict[str, str] = {}
    current_section = "Header"
    section_lines: List[str] = []

    known_headers = [
        "professional summary", "summary", "profile", "objective", "about", "overview",
        "technical skills", "skills", "core competencies", "skills & tools", "skills and tools",
        "professional experience", "experience", "work experience", "employment history", "career history",
        "education", "academic background", "education & certifications", "academic history",
        "certifications", "licenses & certifications", "licenses and certifications", "projects",
        "awards", "honors", "publications"
    ]

    for line in lines:
        s_line = line.strip().rstrip(":#-")
        is_header = False
        header_name = ""

        # Markdown header (H1/H2 for top-level sections; H3/H4 are jobs/sub-entries)
        md_match = re.match(r"^(?:#{1,2}\s+)(.+)$", line.strip())
        if md_match:
            candidate_h = md_match.group(1).strip("#: ")
            if candidate_h.lower() in known_headers or len(candidate_h) < 45:
                is_header = True
                header_name = candidate_h.title()

        if not is_header:
            if s_line.lower() in known_headers:
                is_header = True
                header_name = s_line.title()
            elif 4 <= len(s_line) <= 40 and s_line.isupper() and any(w in s_line.lower() for w in ["experience", "education", "skills", "summary", "certifications", "projects", "competencies"]):
                is_header = True
                header_name = s_line.title()

        if is_header:
            if section_lines:
                sections[current_section] = "\n".join(section_lines).strip()
                section_lines = []
            current_section = header_name
        else:
            section_lines.append(line)

    if section_lines:
        sections[current_section] = "\n".join(section_lines).strip()

    return sections


class BaseParser(ABC):
    """Abstract base class for resume and job description parsers."""

    @abstractmethod
    def parse_file(self, file_path: Path) -> ParsedDocument:
        """Parses a file from path and returns a ParsedDocument."""
        pass

    @abstractmethod
    def parse_text(self, text: str) -> ParsedDocument:
        """Parses raw text content and returns a ParsedDocument."""
        pass

