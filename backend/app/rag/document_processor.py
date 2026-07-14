"""Document processor for parsing various file types"""
import os
from typing import List, Optional
from pathlib import Path
from dataclasses import dataclass

from app.constants import (
    FILE_TYPE_PDF, FILE_TYPE_DOCX, FILE_TYPE_TXT,
    FILE_TYPE_MD, FILE_TYPE_HTML, SUPPORTED_FILE_TYPES
)


@dataclass
class DocumentChunk:
    """Represents a chunk of text from a document"""
    content: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None


class DocumentProcessor:
    """Process documents and extract text content"""

    @staticmethod
    def process(file_path: str, file_type: str) -> List[DocumentChunk]:
        """Process a document and return list of text chunks."""
        if file_type not in SUPPORTED_FILE_TYPES:
            raise ValueError(f"Unsupported file type: {file_type}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_type == FILE_TYPE_PDF:
            return DocumentProcessor._process_pdf(file_path)
        elif file_type == FILE_TYPE_DOCX:
            return DocumentProcessor._process_docx(file_path)
        elif file_type == FILE_TYPE_TXT:
            return DocumentProcessor._process_txt(file_path)
        elif file_type == FILE_TYPE_MD:
            return DocumentProcessor._process_md(file_path)
        elif file_type == FILE_TYPE_HTML:
            return DocumentProcessor._process_html(file_path)

        raise ValueError(f"No processor for file type: {file_type}")

    @staticmethod
    def _process_pdf(file_path: str) -> List[DocumentChunk]:
        """Process PDF file."""
        chunks = []
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                if text:
                    chunks.append(DocumentChunk(
                        content=text.strip(),
                        page_number=page_num
                    ))
        except ImportError:
            raise ImportError("pypdf is required for PDF processing. Install with: pip install pypdf")
        return chunks

    @staticmethod
    def _process_docx(file_path: str) -> List[DocumentChunk]:
        """Process DOCX file."""
        chunks = []
        try:
            from docx import Document
            doc = Document(file_path)
            content_parts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    content_parts.append(para.text.strip())
            if content_parts:
                chunks.append(DocumentChunk(content="\n\n".join(content_parts)))
        except ImportError:
            raise ImportError("python-docx is required for DOCX processing. Install with: pip install python-docx")
        return chunks

    @staticmethod
    def _process_txt(file_path: str) -> List[DocumentChunk]:
        """Process TXT file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if content:
            return [DocumentChunk(content=content.strip())]
        return []

    @staticmethod
    def _process_md(file_path: str) -> List[DocumentChunk]:
        """Process Markdown file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if content:
            return [DocumentChunk(content=content.strip())]
        return []

    @staticmethod
    def _process_html(file_path: str) -> List[DocumentChunk]:
        """Process HTML file."""
        try:
            from bs4 import BeautifulSoup
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            text = soup.get_text(separator='\n\n')
            if text:
                return [DocumentChunk(content=text.strip())]
        except ImportError:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            if content:
                return [DocumentChunk(content=content.strip())]
        return []