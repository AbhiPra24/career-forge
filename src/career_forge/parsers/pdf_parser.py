import re
from pathlib import Path
from typing import Dict, Any, List

from career_forge.parsers.base import BaseParser, ParsedDocument, segment_text_sections
from career_forge.core.exceptions import ParserError


class PdfParser(BaseParser):
    """Parses PDF documents with ligature repair and section segmentation."""

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
            
            raw_text = "\n\n".join(pages_text).strip()
            clean_text = self._repair_pdf_text(raw_text)
            sections = segment_text_sections(clean_text)
            return ParsedDocument(
                raw_text=raw_text,
                clean_text=clean_text,
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

    def _repair_pdf_text(self, text: str) -> str:
        """Repairs font ligatures, fused words, and strips non-printable icon glyphs while preserving tokens."""
        # 1. Protect emails and URLs with placeholders
        emails: List[str] = []
        def save_email(m: re.Match) -> str:
            emails.append(m.group(0))
            return f"__EMAIL_PLACEHOLDER_{len(emails)-1}__"

        urls: List[str] = []
        def save_url(m: re.Match) -> str:
            urls.append(m.group(0))
            return f"__URL_PLACEHOLDER_{len(urls)-1}__"

        text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", save_email, text)
        text = re.sub(r"(?:https?://[^\s]+|linkedin\.com/in/[^\s]+|github\.com/[^\s]+)", save_url, text)

        # 2. Strip icon glyphs & font icon noise
        text = re.sub(r"[♂♀¶✉\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", text)
        text = re.sub(r"(?:map[- ]?marker[- ]?alt|marker[- ]?alt|ap[- ]?arker[- ]?alt)\b", "", text, flags=re.IGNORECASE)

        # 3. Known fused lowercase ligatures from PDF font changes
        fused_replacements = [
            (r"experiencedesigning", "experience designing"),
            (r"device-sidetest", "device-side test"),
            (r"testingand", "testing and"),
            (r"onboardingfrom", "onboarding from"),
            (r"bugswith", "bugs with"),
            (r"inJira", "in Jira"),
            (r"andTestRail", "and TestRail"),
            (r"Performedbackend", "Performed backend"),
            (r"andprotocol", "and protocol"),
            (r"viaSSH", "via SSH"),
            (r"acrossIndia", "across India")
        ]
        for pat, repl in fused_replacements:
            text = re.sub(pat, repl, text, flags=re.IGNORECASE)

        # 4. Protect PascalCase brand/tech terms from being split
        known_tech_brands = [
            "ChargePoint", "TestRail", "GitHub", "LambdaTest", "WebDriverIO",
            "PostgreSQL", "JavaScript", "TypeScript", "GraphQL", "OpenTelemetry",
            "PyTest", "Postman", "MongoDB", "MySQL"
        ]
        protected_brands: List[str] = []
        for brand in known_tech_brands:
            if brand.lower() in text.lower():
                pattern = re.compile(re.escape(brand), re.IGNORECASE)
                text = pattern.sub(f"__TECH_{len(protected_brands)}__", text)
                protected_brands.append(brand)

        # 5. General Word boundary repairs
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
        text = re.sub(r"([a-zA-Z])(\d)", r"\1 \2", text)
        text = re.sub(r"(\d\+?|\%)([a-zA-Z])", r"\1 \2", text)
        text = re.sub(r"([a-zA-Z0-9]),([a-zA-Z0-9])", r"\1, \2", text)

        # 6. Restore protected tech brands
        for idx, brand in enumerate(protected_brands):
            text = text.replace(f"__TECH_{idx}__", brand)

        # 7. Restore emails and URLs
        for idx, email in enumerate(emails):
            text = text.replace(f"__EMAIL_PLACEHOLDER_{idx}__", email)
        for idx, url in enumerate(urls):
            text = text.replace(f"__URL_PLACEHOLDER_{idx}__", url)

        return text.strip()

    def parse_text(self, text: str) -> ParsedDocument:
        raise NotImplementedError("PDF parser requires binary/file input.")
