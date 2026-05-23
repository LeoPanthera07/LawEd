import os
import json
from sqlalchemy.orm import Session
from backend.models import CaseSubmission, LegalReference
import httpx

def run_legal_agent(db: Session, case_id: int, api_key: str = None, provider: str = "groq") -> dict:
    """
    Legal Agent: Executes agentic RAG to find relevant BNS (penal), BSA (evidence), 
    and BNSS (procedural) legal sections that map to the case.
    Supports a fully dynamic live LLM RAG search (BYOK) or a highly-comprehensive offline keyword matcher.
    """
    case = db.query(CaseSubmission).filter(CaseSubmission.id == case_id).first()
    if not case:
        raise ValueError(f"Case with ID {case_id} not found.")

    grievance_text = case.grievance

    # If API Key is provided, execute a real dynamic LLM RAG statutory search
    if api_key:
        try:
            matched_statutes = call_llm_for_statutory_rag(grievance_text, api_key, provider)
            save_legal_references(db, case_id, matched_statutes)
            return {
                "status": "success",
                "agent": "Legal Agent",
                "matched_count": len(matched_statutes),
                "statutes": [s["section_number"] + " " + s["act_title"] for s in matched_statutes]
            }
        except Exception as e:
            # Fallback to simulation/offline mode on error
            pass

    # Read statutes database
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STATUTES_PATH = os.path.join(BASE_DIR, "static_data", "statutes.json")
    with open(STATUTES_PATH, "r", encoding="utf-8") as f:
        statutes = json.load(f)

    # Perform comprehensive keyword-based RAG offline matching
    matched_statutes = []
    lower_text = grievance_text.lower()
    
    # 1. Map substantive BNS offenses
    bns_matches = []
    for section in statutes.get("BNS", []):
        sec_num = section["section_number"]
        keywords = []
        if sec_num == "318": # Cheating
            keywords = ["cheat", "scam", "fraud", "fake", "online", "money", "paid", "refund", "cheated", "lured", "payment"]
        elif sec_num == "303": # Theft
            keywords = ["steal", "theft", "stolen", "stole", "cctv", "robbed", "housebreaker", "missing property", "laptop stolen", "purse stolen"]
        elif sec_num == "316": # Breach of trust
            keywords = ["trust", "partner", "misappropriated", "invested", "fiduciary", "breach", "entrusted", "office funds"]
        elif sec_num == "356": # Defamation
            keywords = ["defame", "reputation", "post", "social", "libel", "slander", "abused", "false tweet", "twitter"]
        elif sec_num == "329": # Trespass
            keywords = ["trespass", "land", "broke in", "property", "entered", "encroach", "tenant", "landlord", "flat"]
        elif sec_num == "115": # Simple Hurt
            keywords = ["hurt", "pain", "beaten", "slapped", "punched", "injury", "assault", "hit me"]
        elif sec_num == "117": # Grievous Hurt
            keywords = ["grievous", "fracture", "hospital", "broken bone", "severely beaten", "blinded", "permanent injury", "fractured"]
        elif sec_num == "336": # Forgery
            keywords = ["forged", "forgery", "fake document", "altered", "signature check", "fake contract", "fabricate", "fake id"]
        elif sec_num == "61": # Criminal Conspiracy
            keywords = ["conspiracy", "conspired", "planned together", "nexus", "group of people", "joint plan", "accomplice"]
        elif sec_num == "351": # Criminal Intimidation
            keywords = ["threat", "threatened", "alarm", "intimidated", "kill you", "extort threat", "abuse threat"]
        elif sec_num == "319": # Cheating by Personation
            keywords = ["personation", "pretended", "impersonate", "fake profile", "assumed identity", "impersonated"]
        elif sec_num == "270": # Public Nuisance
            keywords = ["nuisance", "pollution", "blocked", "garbage", "loudspeaker", "obstructed public"]

        if any(k in lower_text for k in keywords):
            bns_matches.append(section)

    # Fallback to BNS Cheating (Sec 318) or Theft (Sec 303) if nothing matches
    if not bns_matches:
        if "steal" in lower_text or "theft" in lower_text:
            bns_matches.append([s for s in statutes.get("BNS", []) if s["section_number"] == "303"][0])
        else:
            bns_matches.append([s for s in statutes.get("BNS", []) if s["section_number"] == "318"][0])

    # Automatically add conspiracy (Sec 61) if multiple suspects are mentioned (e.g. "they", "accused partners", "dealers")
    if ("they" in lower_text or "dealers" in lower_text or "accomplices" in lower_text) and not any(s["section_number"] == "61" for s in bns_matches):
        conspiracy_sec = [s for s in statutes.get("BNS", []) if s["section_number"] == "61"]
        if conspiracy_sec:
            bns_matches.append(conspiracy_sec[0])

    matched_statutes.extend(bns_matches)

    # 2. Map BNSS Procedural routes
    bnss_matches = []
    # Trespass, Defamation, Hurt are private complaints or summary trials
    is_private_complaint = any(s["section_number"] in ["356", "329", "270"] for s in bns_matches)
    
    for section in statutes.get("BNSS", []):
        if is_private_complaint and section["section_number"] == "223": # Complaint to Magistrate
            bnss_matches.append(section)
        elif not is_private_complaint and section["section_number"] == "173": # FIR (cognizable)
            bnss_matches.append(section)
        
        # Summary trials apply to petty thefts, trespass, and simple hurt
        if any(s["section_number"] in ["303", "329", "115"] for s in bns_matches) and section["section_number"] == "283":
            bnss_matches.append(section)

    if not bnss_matches:
        bnss_matches.append(statutes.get("BNSS", [])[0]) # Default FIR route

    matched_statutes.extend(bnss_matches)

    # 3. Map BSA Evidence rules
    bsa_matches = []
    has_digital = any(k in lower_text for k in ["screenshot", "whatsapp", "email", "online", "chat", "message", "sms", "phone", "pdf", "bank", "ledger"])
    
    for section in statutes.get("BSA", []):
        if section["section_number"] == "4": # Relevancy is always mapped
            bsa_matches.append(section)
        if has_digital and section["section_number"] == "63": # Electronic admissibility
            bsa_matches.append(section)
        if section["section_number"] == "104": # Burden of proof
            bsa_matches.append(section)

    matched_statutes.extend(bsa_matches)

    # Save to database
    save_legal_references(db, case_id, matched_statutes)
    
    return {
        "status": "success", 
        "agent": "Legal Agent", 
        "matched_count": len(matched_statutes), 
        "statutes": [s["section_number"] + " " + s["act_title"] for s in matched_statutes]
    }

def save_legal_references(db: Session, case_id: int, matched_statutes: list):
    # Clear old legal references first
    db.query(LegalReference).filter(LegalReference.case_id == case_id).delete()

    for item in matched_statutes:
        ref = LegalReference(
            case_id=case_id,
            code_type="BNS" if "Nyaya" in item.get("act_title", "") or "BNS" in item.get("act_title", "") else ("BNSS" if "Nagarik" in item.get("act_title", "") or "BNSS" in item.get("act_title", "") else "BSA"),
            section_number=item["section_number"],
            section_title=item["section_title"],
            act_title=item["act_title"],
            description=item["description"],
            punishment=item.get("punishment"),
            procedural_route=item.get("procedural_route") or item.get("evidence_rule")
        )
        db.add(ref)
    db.commit()

def call_llm_for_statutory_rag(text: str, api_key: str, provider: str) -> list:
    """Invokes the live LLM statutory RAG to extract all relevant BNS/BNSS/BSA sections."""
    system_prompt = (
        "You are an expert Indian statutory RAG engine. Identify all relevant sections from BNS (Bharatiya Nyaya Sanhita, 2023), BNSS (Bharatiya Nagarik Suraksha Sanhita, 2023), and BSA (Bharatiya Sakshya Adhiniyam, 2023) that apply to the user's grievance.\n"
        "Be extremely comprehensive and return EVERY section that is relevant from all three documents. For example, substantive offenses (BNS), procedural filing routes (BNSS), and electronic evidence/admissibility rules (BSA).\n"
        "Return your response ONLY as a JSON object containing a single key \"statutes\", which is a list of objects. Each object in the list must represent a section and have the following keys:\n"
        "- \"section_number\": \"string containing the section number (e.g. '318', '63', '173')\"\n"
        "- \"section_title\": \"string containing the formal section title\"\n"
        "- \"act_title\": \"string containing either 'Bharatiya Nyaya Sanhita, 2023', 'Bharatiya Nagarik Suraksha Sanhita, 2023', or 'Bharatiya Sakshya Adhiniyam, 2023'\"\n"
        "- \"description\": \"string containing a concise legal description of the section\"\n"
        "- \"punishment\": \"string (optional, for BNS sections) outlining the statutory penalty, or null\"\n"
        "- \"evidence_required\": \"list of strings detailing critical evidence requirements to prove this section, or null\"\n"
        "- \"procedural_route\": \"string (optional, for BNSS/BSA sections) explaining filing pathways/rules, or null\"\n"
        "Do NOT include any markdown formatting, code blocks, or backticks. Return raw, clean, properly escaped JSON only."
    )

    if provider == "groq":
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.1-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
    else:  # openai
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

    response = httpx.post(url, headers=headers, json=payload, timeout=25.0)
    response.raise_for_status()
    res = response.json()
    content = res["choices"][0]["message"]["content"]
    data = json.loads(content)
    return data.get("statutes", [])

