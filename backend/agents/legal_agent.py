import os
import json
from sqlalchemy.orm import Session
from backend.models import CaseSubmission, LegalReference

def run_legal_agent(db: Session, case_id: int, api_key: str = None, provider: str = "groq") -> dict:
    """
    Legal Agent: Executes agentic RAG against statutes.json to find relevant
    BNS (penal), BSA (evidence), and BNSS (procedural) legal sections that map to the case.
    """
    case = db.query(CaseSubmission).filter(CaseSubmission.id == case_id).first()
    if not case:
        raise ValueError(f"Case with ID {case_id} not found.")

    grievance_text = case.grievance

    # Read statutes database
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STATUTES_PATH = os.path.join(BASE_DIR, "static_data", "statutes.json")
    with open(STATUTES_PATH, "r", encoding="utf-8") as f:
        statutes = json.load(f)

    # Perform statutory lookup / agentic matching
    matched_statutes = []

    # Simple keyword search inside statutes list to map sections
    lower_text = grievance_text.lower()
    
    # 1. Map substantive BNS offenses
    bns_matches = []
    for section in statutes.get("BNS", []):
        keywords = []
        if section["section_number"] == "318": # Cheating
            keywords = ["cheat", "scam", "fraud", "fake", "online", "money", "paid", "refund", "cheated", "lured"]
        elif section["section_number"] == "303": # Theft
            keywords = ["steal", "theft", "stolen", "stole", "cctv", "robbed", "housebreaker", "missing property"]
        elif section["section_number"] == "316": # Breach of trust
            keywords = ["trust", "partner", "misappropriated", "invested", "fiduciary", "breach", "entrusted"]
        elif section["section_number"] == "356": # Defamation
            keywords = ["defame", "reputation", "post", "social", "libel", "slander", "abused"]
        elif section["section_number"] == "329": # Trespass
            keywords = ["trespass", "land", "broke in", "property", "entered", "encroach", "tenant"]

        if any(k in lower_text for k in keywords):
            bns_matches.append(section)

    # Fallback to Cheating (Sec 318) or General if no section matched
    if not bns_matches:
        # Default fallback depending on keywords
        if "steal" in lower_text or "theft" in lower_text:
            bns_matches.append([s for s in statutes.get("BNS", []) if s["section_number"] == "303"][0])
        else:
            bns_matches.append([s for s in statutes.get("BNS", []) if s["section_number"] == "318"][0])

    matched_statutes.extend(bns_matches)

    # 2. Map BNSS Procedural routes
    # Map Section 173 for almost all cognizable, and Section 223 for Private complaints (if civil/trespass or defamation)
    bnss_matches = []
    is_private_complaint = any(s["section_number"] in ["356", "329"] for s in bns_matches) # Defamation/Trespass are often filed via private complaint
    
    for section in statutes.get("BNSS", []):
        if is_private_complaint and section["section_number"] == "223": # Private complaint
            bnss_matches.append(section)
        elif not is_private_complaint and section["section_number"] == "173": # FIR
            bnss_matches.append(section)
        # Summary trials apply to petty thefts/trespass
        if any(s["section_number"] in ["303", "329"] for s in bns_matches) and section["section_number"] == "283":
            bnss_matches.append(section)

    if not bnss_matches:
        bnss_matches.append(statutes.get("BNSS", [])[0]) # Default FIR route

    matched_statutes.extend(bnss_matches)

    # 3. Map BSA Evidence rules
    # Map Section 63 if digital evidence (screenshots, whatsapp, emails, online) is involved
    bsa_matches = []
    has_digital = any(k in lower_text for k in ["screenshot", "whatsapp", "email", "online", "chat", "message", "sms", "phone"])
    
    for section in statutes.get("BSA", []):
        if section["section_number"] == "4": # Relevancy is always mapped
            bsa_matches.append(section)
        if has_digital and section["section_number"] == "63": # Digital records
            bsa_matches.append(section)
        if section["section_number"] == "104": # Burden of proof is always mapped
            bsa_matches.append(section)

    matched_statutes.extend(bsa_matches)

    # Save to database
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
    
    return {
        "status": "success", 
        "agent": "Legal Agent", 
        "matched_count": len(matched_statutes), 
        "statutes": [s["section_number"] + " " + s["act_title"] for s in matched_statutes]
    }
