import time
from sqlalchemy.orm import Session
from backend.models import CaseSubmission
from backend.agents.intake_agent import run_intake_agent
from backend.agents.evidence_agent import run_evidence_agent
from backend.agents.legal_agent import run_legal_agent
from backend.agents.review_agent import run_review_agent
from backend.agents.drafting_agent import run_drafting_agent
from backend.agents.plaintiff_agent import run_plaintiff_agent
from backend.agents.defense_agent import run_defense_agent
from backend.agents.judge_agent import run_judge_agent

def orchestrate_case_analysis(db: Session, case_id: int, api_key: str = None, provider: str = "groq") -> dict:
    """
    Central Orchestrator: Coordinates sequential execution of specialised agents 
    based on the Case Submission's user persona (individual or lawfirm).
    Yields step progress in detail.
    """
    case = db.query(CaseSubmission).filter(CaseSubmission.id == case_id).first()
    if not case:
        raise ValueError(f"Case with ID {case_id} not found.")

    persona = case.user_persona
    steps_log = []

    # Step 1: Intake Fact Extraction
    case.active_step = "intake"
    db.commit()
    intake_res = run_intake_agent(db, case_id, api_key, provider)
    steps_log.append({"step": "Intake Extraction", "status": "completed", "details": "Extracted key facts, timeline, and parties from the grievance."})
    time.sleep(0.5)

    # Step 2: Evidence Review
    case.active_step = "evidence"
    db.commit()
    evidence_res = run_evidence_agent(db, case_id, api_key, provider)
    steps_log.append({"step": "Evidence Review", "status": "completed", "details": "Analyzed and rated uploaded evidence support credibility."})
    time.sleep(0.5)

    # Step 3: Statutory Mapping (RAG)
    case.active_step = "legal_mapping"
    db.commit()
    legal_res = run_legal_agent(db, case_id, api_key, provider)
    steps_log.append({"step": "Statutory Mapping (RAG)", "status": "completed", "details": "Mapped substantive and procedural acts under BNS, BSA, and BNSS."})
    time.sleep(0.5)

    # Step 4: Completeness Review
    case.active_step = "review"
    db.commit()
    review_res = run_review_agent(db, case_id, api_key, provider)
    steps_log.append({"step": "Case Integrity Review", "status": "completed", "details": "Evaluated gaps, highlighted legal risks, and flagged BSA digital evidence requirements."})
    time.sleep(0.5)

    # Step 5: Draft Package Creation
    case.active_step = "drafting"
    db.commit()
    draft_res = run_drafting_agent(db, case_id, api_key, provider)
    steps_log.append({"step": "Draft Brief Construction", "status": "completed", "details": "Compiled pre-filing Case Brief / Preparation package."})
    time.sleep(0.5)

    # If Law Firm persona, execute the courtroom agents (LLM Court)
    if persona == "lawfirm":
        # Step 6: Plaintiff Counsel Opening
        case.active_step = "courtroom_plaintiff"
        db.commit()
        plaintiff_res = run_plaintiff_agent(db, case_id, api_key, provider)
        steps_log.append({"step": "Prosecution Counsel Argument", "status": "completed", "details": "Plaintiff lawyer submitted aggressive opening arguments citing BNS and BSA."})
        time.sleep(0.5)

        # Step 7: Defense Counsel Objection
        case.active_step = "courtroom_defense"
        db.commit()
        defense_res = run_defense_agent(db, case_id, api_key, provider)
        steps_log.append({"step": "Defense Counsel Objection", "status": "completed", "details": "Defense lawyer submitted counter-challenges challenging digital evidence integrity under Section 63 BSA."})
        time.sleep(0.5)

        # Step 8: Adjudicating Judge verdict
        case.active_step = "courtroom_judge"
        db.commit()
        judge_res = run_judge_agent(db, case_id, api_key, provider)
        steps_log.append({"step": "Adjudicating Judicial Evaluation", "status": "completed", "details": "Hon'ble Judicial Magistrate ruled on prima facie case, calculated win probability, and compiled opponent strategy report."})
        time.sleep(0.5)

    case.active_step = "completed"
    db.commit()
    
    return {
        "status": "success",
        "case_id": case_id,
        "persona": persona,
        "steps": steps_log
    }
