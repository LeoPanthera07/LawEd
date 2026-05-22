import json
from sqlalchemy.orm import Session
from backend.models import CaseSubmission, FactExtraction, LegalReference, EvidenceItem, CourtDebateLog
import httpx

def run_defense_agent(db: Session, case_id: int, api_key: str = None, provider: str = "groq") -> str:
    """
    Defense Agent: Represents the Accused/Respondent. Critically reviews the case, 
    challenges the evidence admissibility under Section 63 BSA, questions facts, 
    and raises procedural arguments under BNSS.
    """
    case = db.query(CaseSubmission).filter(CaseSubmission.id == case_id).first()
    facts = db.query(FactExtraction).filter(FactExtraction.case_id == case_id).first()
    legal_refs = db.query(LegalReference).filter(LegalReference.case_id == case_id).all()
    evidence = db.query(EvidenceItem).filter(EvidenceItem.case_id == case_id).all()

    facts_list = json.loads(facts.facts_json) if facts and facts.facts_json else []
    
    bns_sections = [ref for ref in legal_refs if ref.code_type == "BNS"]
    bsa_sections = [ref for ref in legal_refs if ref.code_type == "BSA"]

    # Call LLM if available
    if api_key:
        try:
            argument = call_llm_for_defense(case.grievance, facts_list, legal_refs, evidence, api_key, provider)
            save_debate_log(db, case_id, 2, "Defense_Lawyer", argument)
            return argument
        except Exception:
            pass

    # High fidelity simulated defense argument
    argument = generate_simulated_defense_argument(bns_sections, bsa_sections, evidence)
    save_debate_log(db, case_id, 2, "Defense_Lawyer", argument)
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

def call_llm_for_defense(grievance: str, facts: list, legal_refs: list, evidence: list, api_key: str, provider: str) -> str:
    system_prompt = (
        "You are an elite Defense Counsel in India. Draft a powerful opening argument challenging the complainant's assertions.\n"
        "1. Start with formal court address: 'Most Respectfully, we strongly contest...'\n"
        "2. Challenge the substantive offenses under the BNS (Bharatiya Nyaya Sanhita). If it's cheating/fraud, argue that it is a purely civil breach of contract with NO dishonest intent at the inception.\n"
        "3. Strongly challenge the admissibility of the complainant's electronic records under Section 63 BSA (Bharatiya Sakshya Adhiniyam). Argue that screenshots/PDFs are easily fabricated, and they have NOT filed the mandatory Section 63 Digital Evidence Certificate.\n"
        "4. Highlight timeline inconsistencies or general gaps in facts.\n"
        "5. Conclude by praying that this frivolous complaint be dismissed with costs. Keep it under 20 lines, highly professional, sharp, and legally sound."
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

def generate_simulated_defense_argument(bns_sections: list, bsa_sections: list, evidence: list) -> str:
    sections_str = ", ".join([f"Section {s.section_number} BNS" for s in bns_sections])
    
    evidence_challenge = "Complainant has produced absolutely no secondary or corroborating materials."
    if evidence:
        evidence_challenge = f"Complainant relies solely on '{evidence[0].filename}'. My Lord, this is a digital screenshot, which is highly susceptible to modification, cropping, or complete fabrication."

    argument = f"""Most Respectfully, we strongly contest the false and exaggerated narrative presented by the Prosecution. The allegations under {sections_str} are entirely baseless and represent an abuse of the process of this Hon'ble Court.

Firstly, this dispute is purely civil in nature. A subsequent failure to complete a deal or deliver a service represents a contract breach, not a criminal offense. The Prosecution has shown zero evidence of dishonest intention (mens rea) existing AT THE TIME of the transaction.

Secondly, we raise a severe objection to the admissibility of the electronic records under Section 63 of the Bharatiya Sakshya Adhiniyam (BSA), 2023. {evidence_challenge} They have failed to submit the mandatory Section 63 digital integrity certificate. In the absence of this certificate, this electronic evidence is completely inadmissible.

There exists no prima facie criminal case whatsoever. We pray that this Hon'ble Court reject this frivolous complaint and dismiss it with exemplary costs!"""
    return argument
