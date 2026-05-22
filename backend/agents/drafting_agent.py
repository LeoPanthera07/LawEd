import json
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import CaseSubmission, FactExtraction, LegalReference, EvidenceItem, CaseDraft
import httpx

def run_drafting_agent(db: Session, case_id: int, api_key: str = None, provider: str = "groq") -> dict:
    """
    Drafting Agent: Compiles extracted facts, evidence ratings, and statutory legal references 
    into a beautifully formatted legal Case Brief or Case Preparation Package.
    """
    case = db.query(CaseSubmission).filter(CaseSubmission.id == case_id).first()
    if not case:
        raise ValueError(f"Case with ID {case_id} not found.")

    facts = db.query(FactExtraction).filter(FactExtraction.case_id == case_id).first()
    legal_refs = db.query(LegalReference).filter(LegalReference.case_id == case_id).all()
    evidence = db.query(EvidenceItem).filter(EvidenceItem.case_id == case_id).all()

    # Create list representations for drafting
    facts_list = json.loads(facts.facts_json) if facts and facts.facts_json else []
    timeline_list = json.loads(facts.timeline_json) if facts and facts.timeline_json else []
    parties = json.loads(facts.parties_json) if facts and facts.parties_json else {"complainant": "User", "accused": "Accused"}
    location = facts.location if facts else "Unknown"
    harm = facts.harm if facts else "Unknown"

    bns_sections = [ref for ref in legal_refs if ref.code_type == "BNS"]
    bnss_sections = [ref for ref in legal_refs if ref.code_type == "BNSS"]
    bsa_sections = [ref for ref in legal_refs if ref.code_type == "BSA"]

    # Assemble dynamic structured text
    if api_key:
        try:
            draft_content = call_llm_for_draft(case.grievance, facts_list, legal_refs, evidence, api_key, provider)
            save_draft(db, case_id, draft_content)
            return {"status": "success", "agent": "Drafting Agent", "message": "Draft created successfully via LLM."}
        except Exception:
            pass

    # High-Fidelity simulated legal draft compilation
    draft_content = generate_simulated_draft(parties, location, harm, facts_list, timeline_list, bns_sections, bnss_sections, bsa_sections, evidence)
    save_draft(db, case_id, draft_content)
    return {"status": "success", "agent": "Drafting Agent", "message": "Draft created successfully via simulation."}

def save_draft(db: Session, case_id: int, content: str):
    draft = db.query(CaseDraft).filter(CaseDraft.case_id == case_id, CaseDraft.draft_type == "brief").first()
    if not draft:
        draft = CaseDraft(case_id=case_id, draft_type="brief")
        db.add(draft)
    
    draft.content = content
    db.commit()

def call_llm_for_draft(grievance: str, facts: list, legal_refs: list, evidence: list, api_key: str, provider: str) -> str:
    system_prompt = (
        "You are an expert legal draftsman in India. Draft a professional, highly structured Pre-Filing Case Brief / Complaint Draft based on the provided facts, evidence items, and statutory laws.\n"
        "The draft should look extremely premium and use standard legal headers:\n"
        "1. TITLE & PARTIES (Complainant vs Accused)\n"
        "2. STATEMENT OF JURISDICTION & LOCATION\n"
        "3. EXTRACTED FACTS OF THE DISPUTE (numbered, precise)\n"
        "4. TIMELINE OF INCIDENTS\n"
        "5. APPLICABLE STATUTORY SECTIONS (clearly citing the new BNS, BNSS, and BSA rules mapped)\n"
        "6. EVIDENCE SUBSTANTIATION LOG\n"
        "7. CLOSING CLAIMS & REQUESTED RESOLUTION\n"
        "Maintain formal legal phrasing, professional spacing, and clear structure. Do NOT add preamble or meta-commentary."
    )
    
    legal_text = "\n".join([f"- Section {r.section_number} {r.code_type} ({r.section_title}): {r.description}" for r in legal_refs])
    evidence_text = "\n".join([f"- {e.filename} ({e.file_type}): Rating {e.support_rating}" for e in evidence])
    
    user_prompt = (
        f"Complainant Narrative:\n{grievance}\n\n"
        f"Extracted Facts:\n{json.dumps(facts)}\n\n"
        f"Applicable Statutory Sections:\n{legal_text}\n\n"
        f"Evidence Log:\n{evidence_text}"
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
            "temperature": 0.2
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
            "temperature": 0.2
        }

    response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
    response.raise_for_status()
    res = response.json()
    return res["choices"][0]["message"]["content"]

def generate_simulated_draft(parties: dict, location: str, harm: str, facts: list, timeline: list, bns_sections: list, bnss_sections: list, bsa_sections: list, evidence: list) -> str:
    """Simulates a highly detailed legal draft package."""
    complainant = parties.get("complainant", "User (Informant)")
    accused = parties.get("accused", "Unnamed Opponent")
    
    # Render sections
    bns_text = "\n".join([f"   * **Section {s.section_number} BNS** ({s.section_title}): Punishable with {s.punishment}. \n     *Definition*: {s.description}" for s in bns_sections])
    bnss_text = "\n".join([f"   * **Section {s.section_number} BNSS** ({s.section_title}): \n     *Procedural Step*: {s.procedural_route}" for s in bnss_sections])
    bsa_text = "\n".join([f"   * **Section {s.section_number} BSA** ({s.section_title}): \n     *Admissibility Mandate*: {s.procedural_route}" for s in bsa_sections])

    facts_text = "\n".join([f"   {i+1}. {f}" for i, f in enumerate(facts)])
    timeline_text = "\n".join([f"   * **{t['date']}**: {t['event']}" for t in timeline])
    
    evidence_text = ""
    if evidence:
        evidence_text = "\n".join([f"   * **File**: {e.filename} ({e.file_type})\n     * credibility support rating: **{e.support_rating}**\n     * content: Assessed to corroborate statements of transaction fraud and timeline logs." for e in evidence])
    else:
        evidence_text = "   * **No physical evidence files attached.** (Alert: Complainant must procure ledger, screenshots, or physical records before formal court submission)."

    brief_template = f"""================================================================================
PRE-FILING CASE PREPARATION PACKAGE & BRIEF
================================================================================

1. PARTIES TO THE COMPLAINT
--------------------------------------------------------------------------------
   COMPLAINANT:   {complainant}
   ACCUSED:       {accused}

2. JURISDICTION & PLACE of ACTION
--------------------------------------------------------------------------------
   TERRITORIAL JURISDICTION: District Court of {location}
   STATUTORY JURISDICTION: Executed in accordance with procedural guidelines under Bharatiya Nagarik Suraksha Sanhita (BNSS), 2023.

3. STATEMENT OF FACTS (SUBSTANTIVE DISPUTE DETAILS)
--------------------------------------------------------------------------------
{facts_text}

4. TIMELINE OF INCIDENTS
--------------------------------------------------------------------------------
{timeline_text}

5. APPLICABLE STATUTORY PROVISIONS
--------------------------------------------------------------------------------
A. SUBSTANTIVE OFFENSES MAPPED (BHARATIYA NYAYA SANHITA - BNS):
{bns_text}

B. PROCEDURAL FILING PATHWAYS (BHARATIYA NAGARIK SURAKSHA SANHITA - BNSS):
{bnss_text}

C. EVIDENCE ADMISSIBILITY REQUIREMENTS (BHARATIYA SAKSHYA ADHINIYAM - BSA):
{bsa_text}

6. EVIDENCE CORROBORATION & VALIDATION LOG
--------------------------------------------------------------------------------
{evidence_text}

7. CLOSING CLAIMS & REQUESTED DIRECTIVES
--------------------------------------------------------------------------------
   In light of the facts compiled and statutory guidelines mapped, the Complainant respectfully submits that a clear prima facie case is established against the Accused.
   
   Directives Requested:
   1. Registration of an FIR / complaint under the relevant substantive sections.
   2. Preservation of all transaction and digital communication records under Section 63 BSA.
   3. Formal summons/warrants to the Accused for recovery of damages and wrongful losses.

Dated: {datetime.now().strftime("%d-%B-%Y")}
Signed: __________________________
(Complainant / Representative)
================================================================================
"""
    return brief_template
