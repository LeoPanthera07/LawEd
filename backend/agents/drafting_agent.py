import json
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models import CaseSubmission, FactExtraction, LegalReference, EvidenceItem, CaseDraft
import httpx

def run_drafting_agent(db: Session, case_id: int, api_key: str = None, provider: str = "groq") -> dict:
    """
    Drafting Agent: Compiles extracted facts, evidence ratings, and statutory legal references 
    into a formal, high-fidelity Pre-Filing Court Complaint Petition.
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
            draft_content = call_llm_for_draft(case.grievance, facts_list, legal_refs, evidence, api_key, provider, location)
            save_draft(db, case_id, draft_content)
            return {"status": "success", "agent": "Drafting Agent", "message": "Draft created successfully via LLM."}
        except Exception:
            # Fallback to simulation on failure
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

def call_llm_for_draft(grievance: str, facts: list, legal_refs: list, evidence: list, api_key: str, provider: str, location: str) -> str:
    system_prompt = (
        "You are an expert legal draftsman in India. Draft an authentic, professional, and highly formal Pre-Filing Court Complaint Petition / Complaint under Section 173/223 BNSS.\n"
        "The petition MUST follow the standard Indian legal layout:\n"
        "1. COURT HEADING (e.g. 'BEFORE THE STATION HOUSE OFFICER / MAGISTRATE COURT AT [LOCATION]')\n"
        "2. PARTIES SECTION (COMPLAINANT vs ACCUSED SUSPECTS)\n"
        "3. CITATION SECTION (COMPLAINT UNDER SECTION [BNS sections] OF BNS, 2023 READ WITH SECTION [BNSS sections] OF BNSS, 2023)\n"
        "4. 'MOST RESPECTFULLY SHOWETH:' preamble\n"
        "5. Numbered legal statements/facts starting with 'That...'\n"
        "6. Chronological incident timeline block\n"
        "7. Detailed BNS/BNSS/BSA statutory provisions and applicability\n"
        "8. Exhibit Logs (listing screenshots, receipts, or other evidence)\n"
        "9. 'PRAYER' section with clear, formal, lettered legal demands (e.g. registering FIR, summoning suspect)\n"
        "Maintain strict legal phrasing, formal spacing, and professional petitioner signature blocks. Do NOT include any meta-commentary, markdown, backticks, or intro text."
    )
    
    legal_text = "\n".join([f"- Section {r.section_number} {r.code_type} ({r.section_title}): {r.description}" for r in legal_refs])
    evidence_text = "\n".join([f"- {e.filename} ({e.file_type}): Rating {e.support_rating}" for e in evidence])
    
    user_prompt = (
        f"Location of Action: {location}\n\n"
        f"Complainant Grievance:\n{grievance}\n\n"
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
    """Generates a highly structured, authentic Indian pre-filing petition complaint."""
    complainant = parties.get("complainant", "User (Informant)")
    accused = parties.get("accused", "Unnamed Opponent")
    
    bns_sec_nums = "/".join([s.section_number for s in bns_sections])
    bnss_sec_nums = "/".join([s.section_number for s in bnss_sections])
    
    # Format mapped codes citations
    bns_citations = ", ".join([f"Section {s.section_number} BNS (governing {s.section_title})" for s in bns_sections])
    bnss_citations = ", ".join([f"Section {s.section_number} BNSS (prescribing {s.section_title})" for s in bnss_sections])
    bsa_citations = ", ".join([f"Section {s.section_number} BSA (regulating {s.section_title})" for s in bsa_sections])

    facts_text = "\n".join([f"   {i+1}. That {f}" for i, f in enumerate(facts)])
    
    timeline_text = "\n".join([f"   * **{t['date']}**: {t['event']}" for t in timeline])
    
    evidence_text = ""
    if evidence:
        evidence_text = "\n".join([f"   * **Exhibit {i+1}**: {e.filename} ({e.file_type}) — support rating: **{e.support_rating}**" for i, e in enumerate(evidence)])
    else:
        evidence_text = "   * **No physical attachments present at pre-filing.**"

    petition_draft = f"""BEFORE THE STATION HOUSE OFFICER / MAGISTRATE COURT AT {location.upper()}

IN THE MATTER OF:
{complainant.upper()}                                      ... COMPLAINANT / INFORMANT

VERSUS

{accused.upper()}                                          ... ACCUSED SUSPECT(S)


COMPLAINT UNDER SECTION {bns_sec_nums} OF BHARATIYA NYAYA SANHITA (BNS), 2023 READ WITH SECTION {bnss_sec_nums} OF BHARATIYA NAGARIK SURAKSHA SANHITA (BNSS), 2023 FOR INITIATING POLICE INVESTIGATION / SUMMONS.


MOST RESPECTFULLY SHOWETH:

I. JURISDICTION & CAPACITY:
   1. That the Complainant is a resident of {location} and is filing this complaint to seek legal redressal for injuries caused by the fraudulent and criminal acts of the Accused.
   2. That this Hon'ble Authority / Court holds territorial and subject-matter jurisdiction to register this cognizable offense.

II. STATEMENT OF DOCKET FACTS:
{facts_text}

III. CHRONOLOGICAL TIMELINE OF INCIDENTS:
{timeline_text}

IV. APPLICABLE STATUTORY CITATIONS:
   A. SUBSTANTIVE CHARGES (BNS, 2023):
      The actions of the Accused satisfy the ingredients of:
      * {bns_citations}.

   B. PROCEDURAL CHANNELS (BNSS, 2023):
      In accordance with procedural routing, this matter is triable under:
      * {bnss_citations}.

   C. ADMISSIBILITY PROTOCOLS (BSA, 2023):
      Any digital proof attached to this docket will satisfy requirements of:
      * {bsa_citations}.

V. LIST OF EXHIBITS & CORROBORATING PROOF:
{evidence_text}

VI. BRIEF PRAYER FOR DIRECTIVES:
    In light of the facts detailed above and statutory acts mapped, the Complainant most respectfully prays that this Hon'ble Authority / Court may be pleased to:
    
    a) Register a First Information Report (FIR/e-FIR) under Section 173 BNSS or take cognisance of this complaint under Section 223 BNSS against the Accused.
    b) Direct the preservation and forensic analysis of all transaction ledgers and electronic communication threads in accordance with Section 63 BSA.
    c) Issue formal summons or warrants against the Accused to secure appearance and recovery of wrongful losses/remedies.
    d) Pass any other directive or order that this Hon'ble Authority may deem fit in the interest of justice.


DATED: {datetime.now().strftime("%d-%B-%Y")}
PLACE: {location}

COMPLAINANT / INFORMANT

Through: Counsel/Authorized Legal Representative
"""
    return petition_draft
