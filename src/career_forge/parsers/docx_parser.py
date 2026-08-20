"""
Zero-dependency DOCX Parser with sequential XML body traversal (w:p and w:tbl in order)
"""

import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List

from career_forge.parsers.base import BaseParser, ParsedDocument, segment_text_sections
from career_forge.core.exceptions import ParserError

W_NAMESPACE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class DocxParser(BaseParser):
    """
    Parses .docx files by inspecting word/document.xml directly without heavy dependencies.
    Iterates sequentially over top-level body children (w:p and w:tbl) to preserve reading order.
    """

    def parse_file(self, file_path: Path) -> ParsedDocument:
        path = Path(file_path)
        if not path.exists():
            raise ParserError(f"File not found: {path}")

        MAX_XML_SIZE = 15 * 1024 * 1024  # 15 MB limit against zip bombs

        try:
            with zipfile.ZipFile(path, "r") as docx_zip:
                if "word/document.xml" not in docx_zip.namelist():
                    raise ParserError("Invalid .docx file: word/document.xml missing.")
                info = docx_zip.getinfo("word/document.xml")
                if info.file_size > MAX_XML_SIZE:
                    raise ParserError(f"Security: DOCX document XML exceeds maximum allowable size limit ({MAX_XML_SIZE // (1024*1024)}MB).")
                xml_content = docx_zip.read("word/document.xml")
            
            return self._parse_xml(xml_content, str(path))
        except Exception as e:
            raise ParserError(f"Failed to parse DOCX file {path}: {e}") from e

    def parse_text(self, text: str) -> ParsedDocument:
        raise NotImplementedError("DOCX parser requires binary/file input.")

    def _parse_xml(self, xml_bytes: bytes, file_path: str) -> ParsedDocument:
        root = ET.fromstring(xml_bytes)
        body = root.find(f"{W_NAMESPACE}body")
        if body is None:
            return ParsedDocument(raw_text="", clean_text="", file_type="docx", file_path=file_path)

        ordered_chunks: List[str] = []
        tables_extracted: List[List[List[str]]] = []

        for child in body:
            tag = child.tag
            if tag == f"{W_NAMESPACE}p":
                # Paragraph
                text = self._extract_paragraph_text(child)
                if text.strip():
                    ordered_chunks.append(text)
            elif tag == f"{W_NAMESPACE}tbl":
                # Table
                table_grid, table_text = self._extract_table(child)
                if table_grid:
                    tables_extracted.append(table_grid)
                if table_text.strip():
                    ordered_chunks.append(table_text)

        full_text = "\n\n".join(ordered_chunks).strip()
        sections = segment_text_sections(full_text)

        return ParsedDocument(
            raw_text=full_text,
            clean_text=full_text,
            file_type="docx",
            file_path=file_path,
            tables=tables_extracted,
            sections=sections
        )

    def _extract_paragraph_text(self, p_node: ET.Element) -> str:
        texts = []
        for t in p_node.iter(f"{W_NAMESPACE}t"):
            if t.text:
                texts.append(t.text)
        return "".join(texts)

    def _extract_table(self, tbl_node: ET.Element) -> (List[List[str]], str):
        grid: List[List[str]] = []
        text_lines: List[str] = []

        for row_node in tbl_node.findall(f"{W_NAMESPACE}tr"):
            row: List[str] = []
            for cell_node in row_node.findall(f"{W_NAMESPACE}tc"):
                cell_text = "".join(self._extract_paragraph_text(p) for p in cell_node.findall(f"{W_NAMESPACE}p"))
                row.append(cell_text.strip())
            if row:
                grid.append(row)
                text_lines.append(" | ".join(row))

        return grid, "\n".join(text_lines)
