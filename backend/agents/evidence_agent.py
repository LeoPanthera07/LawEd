import os
from sqlalchemy.orm import Session
from backend.models import CaseSubmission, EvidenceItem
import pypdf

def run_evidence_agent(db: Session, case_id: int, api_key: str = None, provider: str = "groq") -> dict:
    """
    Evidence Agent: Reviews all uploaded evidence items, extracts text from files, 
    and rates their support credibility for the case.
    """
    case = db.query(CaseSubmission).filter(CaseSubmission.id == case_id).first()
    if not case:
        raise ValueError(f"Case with ID {case_id} not found.")

    evidence_items = db.query(EvidenceItem).filter(EvidenceItem.case_id == case_id).all()
    if not evidence_items:
        return {"status": "success", "agent": "Evidence Agent", "message": "No evidence uploaded yet."}

    results = []
    for item in evidence_items:
        # Extract text from files if not already done
        if not item.extracted_text and item.file_path and os.path.exists(item.file_path):
            try:
                extracted_text = extract_text_from_file(item.file_path, item.file_type)
                item.extracted_text = extracted_text
            except Exception as e:
                item.extracted_text = f"[Text Extraction Failed: {str(e)}]"

        # Evaluate support rating
        # If API key is available, run an LLM rating evaluation
        if api_key and item.extracted_text:
            try:
                rating = evaluate_evidence_with_llm(item.extracted_text, case.grievance, api_key, provider)
                item.support_rating = rating
            except Exception:
                item.support_rating = determine_mock_support_rating(item.filename, item.extracted_text)
        else:
            item.support_rating = determine_mock_support_rating(item.filename, item.extracted_text)

        db.commit()
        results.append({
            "id": item.id,
            "filename": item.filename,
            "file_type": item.file_type,
            "support_rating": item.support_rating
        })

    return {"status": "success", "agent": "Evidence Agent", "evidence_eval": results}

def extract_text_from_file(file_path: str, file_type: str) -> str:
    """Extracts text depending on the file extension."""
    if "pdf" in file_type.lower() or file_path.endswith(".pdf"):
        text = ""
        reader = pypdf.PdfReader(file_path)
        for page in reader.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
        return text.strip()
    elif "text" in file_type.lower() or "txt" in file_type.lower() or file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    else:
        # Simulated OCR text for image uploads
        return f"[Simulated Image OCR Data]: Visual screenshot of a transaction receipt/communication showing dispute transaction ID, timestamp, and chat details matching the grievance."

def determine_mock_support_rating(filename: str, text: str) -> str:
    """Simulates support rating based on text content and filename keywords."""
    lower_name = filename.lower()
    lower_text = text.lower() if text else ""
    
    if any(k in lower_name or k in lower_text for k in ["receipt", "bill", "invoice", "statement", "payment", "bank"]):
        return "High"
    elif any(k in lower_name or k in lower_text for k in ["chat", "whatsapp", "email", "screenshot", "message"]):
        return "High"
    elif any(k in lower_name or k in lower_text for k in ["agreement", "contract", "deed"]):
        return "High"
    elif any(k in lower_name or k in lower_text for k in ["photo", "image", "cctv", "video"]):
        return "Medium"
    else:
        return "Medium"

def evaluate_evidence_with_llm(extracted_text: str, grievance: str, api_key: str, provider: str) -> str:
    import httpx
    system_prompt = (
        "You are a forensic legal expert. Evaluate how strongly the following extracted evidence text supports the user's grievance.\n"
        "Output ONLY one of the following exact ratings:\n"
        "- High (if it strongly supports financial transfers, clear admissions, or theft acts)\n"
        "- Medium (if it shows partial context but lacks absolute proof)\n"
        "- Low (if it has weak relevance)\n"
        "- Irrelevant (if it does not support the case at all)\n"
        "Do NOT include any extra words, punctuation, or explanations."
    )
    user_prompt = f"Grievance: {grievance}\n\nEvidence Extracted Text:\n{extracted_text}"

    if provider == "groq":
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1
        }
    else:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1
        }

    response = httpx.post(url, headers=headers, json=payload, timeout=15.0)
    response.raise_for_status()
    res = response.json()
    rating = res["choices"][0]["message"]["content"].strip()
    
    for r in ["High", "Medium", "Low", "Irrelevant"]:
        if r.lower() in rating.lower():
            return r
    return "Medium"
