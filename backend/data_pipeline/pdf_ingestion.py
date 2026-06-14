import re
from dataclasses import dataclass
from typing import Optional

import fitz


@dataclass
class ClauseChunk:
    act: str
    chapter: str
    chapter_number: str
    section_number: str
    section_title: str
    clause_text: str
    chunk_index: int
    total_chunks: int
    word_count: int


class LegalPDFIngester:
    MAX_CHUNK_TOKENS = 512
    CHUNK_OVERLAP_TOKENS = 50

    def __init__(self, act_name: str):
        self.act_name = act_name
        self.chunks: list[ClauseChunk] = []

    def ingest(self, pdf_path: str) -> list[ClauseChunk]:
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text("text")
        doc.close()

        sections = self._parse_sections(full_text)
        for section in sections:
            self._chunk_section(section)

        return self.chunks

    def _parse_sections(self, text: str) -> list[dict]:
        sections = []
        current_chapter = ""
        current_chapter_num = ""

        chapter_pattern = re.compile(
            r"CHAPTER\s+([IVXLCDM]+)\s*\n\s*([A-Z][^\n]+)",
            re.MULTILINE,
        )
        section_pattern = re.compile(
            r"^(\d+[A-Z]?)\.\s+([^.\n]+\.)\s*\n(.*?)(?=^\d+[A-Z]?\.|^CHAPTER|\Z)",
            re.MULTILINE | re.DOTALL,
        )

        for chapter_match in chapter_pattern.finditer(text):
            current_chapter_num = chapter_match.group(1)
            current_chapter = chapter_match.group(2).strip()

        for section_match in section_pattern.finditer(text):
            sections.append(
                {
                    "chapter": current_chapter,
                    "chapter_number": current_chapter_num,
                    "section_number": section_match.group(1),
                    "section_title": section_match.group(2).strip(),
                    "full_text": section_match.group(3).strip(),
                }
            )

        return sections

    def _chunk_section(self, section: dict) -> None:
        text = section["full_text"]
        words = text.split()

        if len(words) <= self.MAX_CHUNK_TOKENS:
            self.chunks.append(
                ClauseChunk(
                    act=self.act_name,
                    chapter=section["chapter"],
                    chapter_number=section["chapter_number"],
                    section_number=section["section_number"],
                    section_title=section["section_title"],
                    clause_text=f"{section['section_number']}. {section['section_title']} {text}",
                    chunk_index=0,
                    total_chunks=1,
                    word_count=len(words),
                )
            )
        else:
            chunks = []
            step = self.MAX_CHUNK_TOKENS - self.CHUNK_OVERLAP_TOKENS
            for i in range(0, len(words), step):
                chunk_words = words[i : i + self.MAX_CHUNK_TOKENS]
                chunk_text = " ".join(chunk_words)
                prefixed = f"{section['section_number']}. {section['section_title']} {chunk_text}"
                chunks.append(prefixed)

            for idx, chunk_text in enumerate(chunks):
                self.chunks.append(
                    ClauseChunk(
                        act=self.act_name,
                        chapter=section["chapter"],
                        chapter_number=section["chapter_number"],
                        section_number=section["section_number"],
                        section_title=section["section_title"],
                        clause_text=chunk_text,
                        chunk_index=idx,
                        total_chunks=len(chunks),
                        word_count=len(chunk_text.split()),
                    )
                )
