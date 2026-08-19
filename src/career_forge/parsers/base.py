"""
Abstract Base Parser definition and common data structures
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


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
