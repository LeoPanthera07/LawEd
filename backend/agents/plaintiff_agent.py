import json
from sqlalchemy.orm import Session
from backend.models import CaseSubmission, FactExtraction, LegalReference, EvidenceItem, CourtDebateLog
import httpx

def run_plaintiff_agent(db: Session, case_id: int, api_key: str = None, provider: str = "groq") -> str:
    """
    Plaintiff/Prosecution Agent: Represents the Complainant. Argues the strength of the case,
    citing statutes under BNS, procedural compliance under BNSS, and why evidence is solid.
    """
    case = db.query(CaseSubmission).filter(CaseSubmission.id == case_id).first()
    facts = db.query(FactExtraction).filter(FactExtraction.case_id == case_id).first()
    legal_refs = db.query(LegalReference).filter(LegalReference.case_id == case_id).all()
    evidence = db.query(EvidenceItem).filter(EvidenceItem.case_id == case_id).all()

    facts_list = json.loads(facts.facts_json) if facts and facts.facts_json else []
    timeline_list = json.loads(facts.timeline_json) if facts and facts.timeline_json else []
    location = facts.location if facts else "Unknown"

    bns_sections = [ref for ref in legal_refs if ref.code_type == "BNS"]
    bsa_sections = [ref for ref in legal_refs if ref.code_type == "BSA"]

    # Call LLM if available
    if api_key:
        try:
            argument = call_llm_for_plaintiff(case.grievance, facts_list, legal_refs, evidence, api_key, provider)
            save_debate_log(db, case_id, 1, "Plaintiff_Lawyer", argument)
            return argument
        except Exception:
            pass

    # High fidelity simulated argument
    argument = generate_simulated_plaintiff_argument(bns_sections, bsa_sections, evidence, location)
    save_debate_log(db, case_id, 1, "Plaintiff_Lawyer", argument)
    return argument

def save_debate_log(db: Session, case_id: int, index: int, speaker: str, text: str):
    log = db.query(CourtDebateLog).filter(
        CourtDebateLog.case_id == case_id, 
        CourtDebateLog.speaker == speaker
    ).first()
    
    if not log:
        log = CourtDebateLog(case_id=case_id, argument_index=index, speaker=speaker)
        db.add(log)
    
    log.text = text
    db.commit()

def call_llm_for_plaintiff(grievance: str, facts: list, legal_refs: list, evidence: list, api_key: str, provider: str) -> str:
    system_prompt = (
        "You are an elite Prosecution/Plaintiff Counsel in India. Draft a powerful opening argument presenting the complainant's case to the Court.\n"
        "1. Start with formal court address: 'Respected Judge, we submit...'\n"
        "2. Establish the exact substantive charges under the new BNS (Bharatiya Nyaya Sanhita) code, highlighting the illegal actions of the accused.\n"
        "3. Emphasize why a prima facie case exists, referencing the extracted timeline and facts.\n"
        "4. Argue that the evidence items uploaded are admissible under BSA (Bharatiya Sakshya Adhiniyam) and directly prove the charges.\n"
        "5. Conclude by demanding that the accused be summoned. Keep it under 20 lines, highly dramatic, professional, and legally sound."
    )
    
    legal_text = "\n".join([f"- Section {r.section_number} {r.code_type}: {r.description}" for r in legal_refs])
    evidence_text = "\n".join([f"- {e.filename} ({e.file_type}): Rating {e.support_rating}" for e in evidence])
    
    user_prompt = (
        f"Case facts:\n{json.dumps(facts)}\n\n"
        f"Statutes:\n{legal_text}\n\n"
        f"Evidence Items:\n{evidence_text}"
    )

    if provider == "groq":
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {
            "model": "llama-3.1-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.3
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
            "temperature": 0.3
        }

    response = httpx.post(url, headers=headers, json=payload, timeout=20.0)
    response.raise_for_status()
    res = response.json()
    return res["choices"][0]["message"]["content"]

def generate_simulated_plaintiff_argument(bns_sections: list, bsa_sections: list, evidence: list, location: str) -> str:
    sections_str = ", ".join([f"Section {s.section_number} BNS" for s in bns_sections])
    
    evidence_sentence = "We have submitted primary digital logs which are highly authentic."
    if evidence:
        evidence_sentence = f"We have placed before this Court the record '{evidence[0].filename}' which holds a {evidence[0].support_rating} support rating, showing unquestionable proof."

    argument = f"""My Lord, I represent the Complainant in this matter. We submit before this Court that a clear, undeniable case of criminal liability is established under {sections_str}. 

The facts demonstrate a calculated, malicious course of action by the Accused to cause wrongful loss to my client. Complainant transferred hard-earned funds relying entirely on the false representations made by the Accused, constituting a clear offense of Cheating and Breach of Trust.

Regarding evidence, {evidence_sentence} In compliance with Section 63 of the Bharatiya Sakshya Adhiniyam (BSA), 2023, these electronic records stand fully admissible to establish the fraudulent timeline. There exists a complete prima facie case against the Accused. We pray that this Hon'ble Court take immediate cognizance, register the charges, and issue summons to the Accused to meet the ends of justice!"""
    return argument
