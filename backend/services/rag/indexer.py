import os
import re
import json
import math
import pypdf
from sqlalchemy.orm import Session
from backend.services.rag.database import engine, Base, SessionLocal
from backend.services.rag.models import StatuteChunk

# Create database tables
Base.metadata.create_all(bind=engine)

STOPWORDS = {"the", "a", "an", "and", "in", "of", "to", "for", "by", "on", "is", "it", "with", "that", "this", "or", "as", "at", "be", "from", "shall", "under", "any", "such"}

def tokenize(text: str) -> list:
    """Standardizes, tokenizes, and filters out stopwords from a text block."""
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    return [w for w in words if w not in STOPWORDS]

def clean_spacing(text: str) -> str:
    """
    Cleans up character-spacing kerning artifacts (spaced letters) from PDF extraction.
    Transforms sequences of single-spaced letters back into solid words line-by-line.
    """
    # 1. Clean Gazette footer markers to avoid false section matches
    text = re.sub(r"(?i)Sec\.\s*1\s*\]\s*THE\s+GAZETTE\s+OF\s+INDIA.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"(?i)Sec\.\s*1\s*\]", "", text)
    
    # 2. Reconstruct spaced words line by line to preserve structure
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        chars = list(line)
        n = len(chars)
        i = 0
        while i < n - 1:
            # Shift spaces to the right of the subsequent letter
            if chars[i] == ' ' and chars[i+1] != ' ' and chars[i+1] != '\t':
                chars[i], chars[i+1] = chars[i+1], chars[i]
            i += 1
        cleaned_line = re.sub(r"[ \t]+", " ", "".join(chars)).strip()
        cleaned_lines.append(cleaned_line)
        
    return "\n".join(cleaned_lines)

def calculate_term_frequencies(tokens: list) -> dict:
    """Computes simple term count frequencies for a list of tokens."""
    if not tokens:
        return {}
    freqs = {}
    for t in tokens:
        freqs[t] = freqs.get(t, 0) + 1
    # Standardize by length
    total = len(tokens)
    return {k: v / total for k, v in freqs.items()}

def build_rag_index(db: Session, force_reindex: bool = False):
    """
    Scans the Source/ directory for BNS.pdf, BNSS.pdf, and BSA.pdf.
    Parses pages, chunks text, tokenizes, and indexes them in SQLite if empty.
    """
    # Check if already indexed
    existing_count = db.query(StatuteChunk).count()
    if existing_count > 0 and not force_reindex:
        print(f"RAG Index already populated with {existing_count} chunks. Skipping indexing.")
        return

    # Clear old entries if force_reindex is active
    if force_reindex:
        db.query(StatuteChunk).delete()
        db.commit()

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    SOURCE_DIR = os.path.join(BASE_DIR, "Source")
    
    pdf_files = {
        "BNS": os.path.join(SOURCE_DIR, "BNS.pdf"),
        "BNSS": os.path.join(SOURCE_DIR, "BNSS.pdf"),
        "BSA": os.path.join(SOURCE_DIR, "BSA.pdf")
    }

    chunks_added = 0

    for act_type, pdf_path in pdf_files.items():
        if not os.path.exists(pdf_path):
            print(f"Statutory PDF for {act_type} not found at {pdf_path}. Skipping.")
            continue

        print(f"Indexing PDF: {pdf_path} ...")
        try:
            reader = pypdf.PdfReader(pdf_path)
            total_pages = len(reader.pages)
            
            current_section_num = "unknown"
            current_section_title = "Statute Content"

            for page_num in range(total_pages):
                raw_text = reader.pages[page_num].extract_text()
                if not raw_text:
                    continue
                
                # Clean character spacing kerning artifacts and Gazette footers
                text = clean_spacing(raw_text)

                # Segment page text by paragraphs/sections
                # Scan for section header markings: e.g. "Section 318" or "Cl. 63"
                sec_match = re.findall(r"(?:Section|Sec\.|Cl\.)\s*(\d+[A-Z]*)", text)
                
                # Fallback to definitions like "318.(1)" or "318. (1)" or "318. Cheating" at the start of a line
                if not sec_match:
                    sec_match = re.findall(r"(?:^|\n)\s*(\d+[A-Z]*)\.\s*\(?[a-zA-Z\d]", text)
                
                # Fallback to simple number prefix "318." at start of a line
                if not sec_match:
                    sec_match = re.findall(r"(?:^|\n)\s*(\d+[A-Z]*)\.\s*", text)

                if sec_match:
                    current_section_num = sec_match[0]
                    # Attempt to extract heading title (first line containing the match)
                    lines = text.split("\n")
                    for line in lines:
                        if current_section_num in line and len(line.strip()) < 120:
                            current_section_title = line.strip()[:100]
                            break

                # Create sliding window chunks of 1000 characters with 200 characters overlap
                chunk_size = 1000
                overlap = 200
                idx = 0
                while idx < len(text):
                    chunk_text = text[idx:idx + chunk_size]
                    idx += (chunk_size - overlap)

                    if len(chunk_text.strip()) < 50:
                        continue

                    # Tokenize and compute frequencies
                    tokens = tokenize(chunk_text)
                    if not tokens:
                        continue
                    
                    freqs = calculate_term_frequencies(tokens)

                    statute_chunk = StatuteChunk(
                        act_type=act_type,
                        section_number=current_section_num,
                        section_title=current_section_title,
                        chunk_text=chunk_text.strip(),
                        token_frequencies_json=json.dumps(freqs)
                    )
                    db.add(statute_chunk)
                    chunks_added += 1

                # Commit batch every 50 pages to preserve memory
                if page_num % 50 == 0:
                    db.commit()

            db.commit()
            print(f"Successfully finished indexing {act_type}. Total chunks created so far: {chunks_added}")

        except Exception as e:
            print(f"Error parsing statutory PDF {pdf_path}: {e}")

    print("RAG Statutory Indexing pipeline completed successfully.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        build_rag_index(db, force_reindex=True)
    finally:
        db.close()
