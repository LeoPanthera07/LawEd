import os
import re
import json
import pypdf

def clean_spacing(text: str) -> str:
    """Reconstructs spaced words from PDF kerning issues and removes footer/header noise."""
    # Remove Gazette headers/footers
    text = re.sub(r"(?i)Sec\.\s*1\s*\]\s*THE\s+GAZETTE\s+OF\s+INDIA.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"(?i)THE\s+GAZETTE\s+OF\s+INDIA.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"(?i)Sec\.\s*1\s*\]", "", text)
    
    # Simple letter reconstructor line by line
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        if not line.strip():
            continue
        # Join spaced letters but preserve space between words if they are wider
        # If there are many single letters, e.g., "T h e  c o n d u c t"
        # We can find sequences like a b c and join them
        chars = list(line)
        n = len(chars)
        i = 0
        while i < n - 1:
            if chars[i] == ' ' and chars[i+1] != ' ' and chars[i+1] != '\t':
                # Swap space to the right
                chars[i], chars[i+1] = chars[i+1], chars[i]
            i += 1
        cleaned = "".join(chars)
        # Replace multiple spaces with a single space
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        cleaned_lines.append(cleaned)
    return "\n".join(cleaned_lines)

def scrape_act(pdf_path: str, act_name: str) -> list:
    """Scrapes sections/chapters from the PDF using regex."""
    if not os.path.exists(pdf_path):
        print(f"PDF not found: {pdf_path}")
        return []
        
    print(f"Scraping {act_name} from {pdf_path}...")
    reader = pypdf.PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += clean_spacing(text) + "\n"
            
    # Now, parse sections using regex
    # Sections typically start with:
    # "123. Title text" or "Section 123. Title text" or similar at the beginning of a line
    # Let's search for matches
    sections = []
    
    # We can split text by section markers
    # Pattern to match section numbers at start of line: e.g. "63. Admissibility..." or "Section 63." or "Cl. 63."
    pattern = r"(?:\n|^)\s*(?:\bSection\b|\bSec\.\b|\bCl\.\b)?\s*(\d+[A-Z]*)\.\s*([A-Za-z][^\n]+)"
    matches = list(re.finditer(pattern, full_text))
    
    for i, match in enumerate(matches):
        sec_num = match.group(1)
        sec_title = match.group(2).strip()
        
        # Limit title size to avoid greediness matching entire paragraphs
        if len(sec_title) > 120:
            sec_title = sec_title[:80] + "..."
            
        # The content is the text between this match and the next match
        start_idx = match.end()
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(full_text)
        content = full_text[start_idx:end_idx].strip()
        
        # Clean up content a bit
        content = re.sub(r"\s+", " ", content)
        
        # Evidentiary or procedural tag
        act_title_full = {
            "BNS": "Bharatiya Nyaya Sanhita, 2023",
            "BNSS": "Bharatiya Nagarik Suraksha Sanhita, 2023",
            "BSA": "Bharatiya Sakshya Adhiniyam, 2023"
        }.get(act_name, act_name)
        
        sections.append({
            "section_number": sec_num,
            "section_title": sec_title,
            "content": content,
            "source": act_name,
            "act_title": act_title_full
        })
        
    print(f"Scraped {len(sections)} sections from {act_name}.")
    return sections

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    source_dir = os.path.join(base_dir, "Source")
    static_dir = os.path.join(base_dir, "backend", "static_data")
    
    pdf_files = {
        "BNS": os.path.join(source_dir, "BNS.pdf"),
        "BNSS": os.path.join(source_dir, "BNSS.pdf"),
        "BSA": os.path.join(source_dir, "BSA.pdf")
    }
    
    all_sections = {}
    for act_name, pdf_path in pdf_files.items():
        all_sections[act_name] = scrape_act(pdf_path, act_name)
        
    output_path = os.path.join(static_dir, "scraped_statutes.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_sections, f, indent=2, ensure_ascii=False)
    print(f"Successfully wrote all sections to {output_path}")

if __name__ == "__main__":
    main()
