"""Text chunker for splitting documents into smaller pieces"""
from typing import List
from dataclasses import dataclass
import re

from app.config import settings


@dataclass
class Chunk:
    """Represents a text chunk with metadata"""
    text: str
    chunk_index: int
    document_id: int
    start_char: int = 0
    end_char: int = 0


class TextChunker:
    """Split text into chunks for embedding"""

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def chunk_text(
        self,
        text: str,
        document_id: int,
        strategy: str = "by_paragraph"
    ) -> List[Chunk]:
        """Split text into chunks based on strategy."""
        if strategy == "by_paragraph":
            return self._chunk_by_paragraph(text, document_id)
        elif strategy == "by_page":
            return self._chunk_by_page(text, document_id)
        else:
            return self._chunk_by_size(text, document_id)

    def _chunk_by_paragraph(self, text: str, document_id: int) -> List[Chunk]:
        """Split text by paragraphs with size constraints."""
        chunks = []
        paragraphs = re.split(r'\n\s*\n', text)
        current_chunk = ""
        chunk_index = 0
        start_char = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(Chunk(
                        text=current_chunk.strip(),
                        chunk_index=chunk_index,
                        document_id=document_id,
                        start_char=start_char,
                        end_char=start_char + len(current_chunk)
                    ))
                    chunk_index += 1
                    start_char += len(current_chunk)

                if len(para) > self.chunk_size:
                    chunks.extend(self._chunk_long_text(para, document_id, chunk_index, start_char))
                    chunk_index = chunks[-1].chunk_index + 1 if chunks else chunk_index
                    start_char = chunks[-1].end_char if chunks else start_char
                else:
                    current_chunk = para + "\n\n"

        if current_chunk.strip():
            chunks.append(Chunk(
                text=current_chunk.strip(),
                chunk_index=chunk_index,
                document_id=document_id,
                start_char=start_char,
                end_char=start_char + len(current_chunk)
            ))

        return chunks

    def _chunk_by_page(self, text: str, document_id: int) -> List[Chunk]:
        """Split text by pages (assumes page markers in text)."""
        pages = re.split(r'(?:Page \d+|--- Page \d+ ---)', text, flags=re.IGNORECASE)
        chunks = []
        for idx, page in enumerate(pages):
            if page.strip():
                page_text = page.strip()
                if len(page_text) > self.chunk_size:
                    sub_chunks = self._chunk_long_text(page_text, document_id, idx, 0)
                    chunks.extend(sub_chunks)
                else:
                    chunks.append(Chunk(
                        text=page_text,
                        chunk_index=idx,
                        document_id=document_id
                    ))
        return chunks

    def _chunk_by_size(self, text: str, document_id: int) -> List[Chunk]:
        """Split text by fixed size with overlap."""
        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            if start > 0:
                overlap_start = start - self.chunk_overlap
                if overlap_start < 0:
                    overlap_start = 0
                chunk_text = text[overlap_start:end]

            chunks.append(Chunk(
                text=chunk_text.strip(),
                chunk_index=chunk_index,
                document_id=document_id,
                start_char=start,
                end_char=end
            ))

            start = end - self.chunk_overlap
            chunk_index += 1

        return chunks

    def _chunk_long_text(
        self,
        text: str,
        document_id: int,
        start_index: int,
        start_char: int
    ) -> List[Chunk]:
        """Handle text that exceeds chunk size."""
        chunks = []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        current_chunk = ""
        chunk_index = start_index
        char_offset = start_char

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(Chunk(
                        text=current_chunk.strip(),
                        chunk_index=chunk_index,
                        document_id=document_id,
                        start_char=char_offset,
                        end_char=char_offset + len(current_chunk)
                    ))
                    chunk_index += 1
                    char_offset += len(current_chunk)
                current_chunk = sentence + " "

        if current_chunk.strip():
            chunks.append(Chunk(
                text=current_chunk.strip(),
                chunk_index=chunk_index,
                document_id=document_id,
                start_char=char_offset,
                end_char=char_offset + len(current_chunk)
            ))

        return chunks