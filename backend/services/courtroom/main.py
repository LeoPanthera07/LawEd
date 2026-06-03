import os
import shutil
import uuid
import json
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.services.courtroom.database import engine, Base, get_db
from backend.services.courtroom.models import CaseSubmission, EvidenceItem, FactExtraction, LegalReference, CourtDebateLog, CaseDraft, ReviewFlag, LegalInterpretation, PrecedentMatch

# Import the agents (they use local orchestrator steps)
from backend.agents.intake_agent import run_intake_agent
from backend.agents.evidence_agent import run_evidence_agent
from backend.agents.legal_agent import run_legal_agent
from backend.agents.review_agent import run_review_agent
from backend.agents.drafting_agent import run_drafting_agent
from backend.agents.plaintiff_agent import run_plaintiff_agent
from backend.agents.defense_agent import run_defense_agent
from backend.agents.judge_agent import run_judge_agent
from backend.agents.interpretation_agent import run_interpretation_agent

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LawEdAI Courtroom & Case Simulation Service",
    description="Microservice coordinating case submissions, UNIQUE-ID lookups, and multi-agent simulations."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/cases")
def create_case(
    grievance: str = Form(...),
    location: Optional[str] = Form(None),
    citizen_id: Optional[int] = Form(None),
    acquired_by_firm_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    """Creates a new case, generates a UNIQUE-ID, and runs baseline analysis or full courtroom simulation."""
    unique_id = f"LAWED-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
    
    is_firm = acquired_by_firm_id is not None
    persona = "lawfirm" if is_firm else "individual"
    step = "courtroom_debate" if is_firm else "intake"
    
    case = CaseSubmission(
        grievance=grievance,
        location=location,
        citizen_id=citizen_id,
        acquired_by_firm_id=acquired_by_firm_id,
        unique_id=unique_id,
        user_persona=persona,
        active_step=step
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    # Trigger Baseline Pipeline
    try:
        run_intake_agent(db, case.id)
        run_evidence_agent(db, case.id)
        run_legal_agent(db, case.id)
        run_interpretation_agent(db, case.id)
        run_drafting_agent(db, case.id)
        
        if is_firm:
            # Trigger Adjudication Courtroom Simulation Pipeline for Law Firms
            run_review_agent(db, case.id)
            run_plaintiff_agent(db, case.id)
            run_defense_agent(db, case.id)
            run_judge_agent(db, case.id)
        else:
            run_judge_agent(db, case.id) # Calculates baseline case strength win probability
            
        case.active_step = "completed"
        db.commit()
    except Exception as e:
        print(f"Error executing case pipeline: {e}")

    return {
        "status": "success",
        "case_id": case.id,
        "unique_id": case.unique_id,
        "persona": case.user_persona
    }

@app.post("/api/cases/{case_id}/evidence")
def upload_evidence(
    case_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Uploads evidence items for a specific case dockets folder."""
    case = db.query(CaseSubmission).filter(CaseSubmission.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    case_upload_dir = os.path.join(UPLOAD_DIR, str(case_id))
    os.makedirs(case_upload_dir, exist_ok=True)

    evidence_list = []
    for file in files:
        file_path = os.path.join(case_upload_dir, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        evidence = EvidenceItem(
            case_id=case_id,
            filename=file.filename,
            file_type=file.content_type or "application/octet-stream",
            file_path=file_path,
            support_rating="Medium"
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        
        evidence_list.append({
            "id": evidence.id,
            "filename": evidence.filename,
            "file_type": evidence.file_type
        })

    # Recalculate baseline evidence ratings
    try:
        run_evidence_agent(db, case_id)
        run_judge_agent(db, case_id)
    except Exception as e:
        print(f"Error updating evidence ratings: {e}")

    return {"status": "success", "uploaded_evidence": evidence_list}

@app.post("/api/cases/acquire")
def acquire_case(payload: dict, db: Session = Depends(get_db)):
    """Law Firm Case Acquisition: Matches UNIQUE-ID and triggers adversarial courtroom simulations."""
    unique_id = payload.get("unique_id", "").strip().upper()
    firm_id = payload.get("acquired_by_firm_id")

    if not unique_id or not firm_id:
        raise HTTPException(status_code=400, detail="Missing UNIQUE-ID or firm ID.")

    case = db.query(CaseSubmission).filter(CaseSubmission.unique_id == unique_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Grievance dossier with this UNIQUE-ID not found.")

    # Mark as acquired and switch persona
    case.acquired_by_firm_id = firm_id
    case.user_persona = "lawfirm"
    case.active_step = "courtroom_debate"
    db.commit()

    # Trigger Phase 2 Law Firm Pipeline: Simulated Courtroom Battle
    try:
        run_review_agent(db, case.id)
        run_plaintiff_agent(db, case.id)
        run_defense_agent(db, case.id)
        run_judge_agent(db, case.id) # Adjudicates courtroom battle and provides litigation briefs
        
        case.active_step = "completed"
        db.commit()
    except Exception as e:
        print(f"Error executing Adjudication pipeline: {e}")

    return {
        "status": "success",
        "case_id": case.id,
        "unique_id": case.unique_id,
        "persona": case.user_persona
    }

@app.get("/api/cases/{case_id}/dashboard")
def get_dashboard(case_id: int, db: Session = Depends(get_db)):
    """Fetches full processed legal dashboard parameters for a case dockets view."""
    case = db.query(CaseSubmission).filter(CaseSubmission.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    facts = db.query(FactExtraction).filter(FactExtraction.case_id == case_id).first()
    legal_refs = db.query(LegalReference).filter(LegalReference.case_id == case_id).all()
    evidence = db.query(EvidenceItem).filter(EvidenceItem.case_id == case_id).all()
    flags = db.query(ReviewFlag).filter(ReviewFlag.case_id == case_id).all()
    brief_draft = db.query(CaseDraft).filter(CaseDraft.case_id == case_id, CaseDraft.draft_type == "brief").first()
    strategy_draft = db.query(CaseDraft).filter(CaseDraft.case_id == case_id, CaseDraft.draft_type == "strategy_report").first()
    interpretations = db.query(LegalInterpretation).filter(LegalInterpretation.case_id == case_id).all()
    precedents = db.query(PrecedentMatch).filter(PrecedentMatch.case_id == case_id).all()
    debate_logs = db.query(CourtDebateLog).filter(CourtDebateLog.case_id == case_id).order_by(CourtDebateLog.argument_index).all()

    return {
        "case_id": case.id,
        "unique_id": case.unique_id,
        "grievance": case.grievance,
        "location": case.location,
        "created_at": case.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "user_persona": case.user_persona,
        "active_step": case.active_step,
        "win_probability": case.win_probability,
        "judge_verdict": case.judge_verdict,
        "facts": json.loads(facts.facts_json) if facts and facts.facts_json else [],
        "timeline": json.loads(facts.timeline_json) if facts and facts.timeline_json else [],
        "parties": json.loads(facts.parties_json) if facts and facts.parties_json else {"complainant": "User", "accused": "Opponent"},
        "harm": facts.harm if facts else "Unknown",
        "statutes": [
            {
                "code_type": r.code_type,
                "section_number": r.section_number,
                "section_title": r.section_title,
                "act_title": r.act_title,
                "description": r.description,
                "punishment": r.punishment,
                "procedural_route": r.procedural_route
            }
            for r in legal_refs
        ],
        "evidence": [
            {
                "id": e.id,
                "filename": e.filename,
                "file_type": e.file_type,
                "support_rating": e.support_rating
            }
            for e in evidence
        ],
        "flags": [
            {
                "flag_type": f.flag_type,
                "flag_title": f.flag_title,
                "message": f.message,
                "severity": f.severity
            }
            for f in flags
        ],
        "interpretations": [
            {
                "clause_number": i.clause_number,
                "act_title": i.act_title,
                "user_fact_mapping": i.user_fact_mapping,
                "legal_opinion": i.legal_opinion
            }
            for i in interpretations
        ],
        "precedents": [
            {
                "citation": p.citation,
                "case_name": p.case_name,
                "year": p.year,
                "court": p.court,
                "summary": p.summary,
                "relevance": p.relevance
            }
            for p in precedents
        ],
        "case_brief": brief_draft.content if brief_draft else None,
        "strategy_report": strategy_draft.content if strategy_draft else None,
        "debate_logs": [
            {
                "speaker": log.speaker,
                "text": log.text,
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for log in debate_logs
        ]
    }

@app.get("/api/cases")
def list_cases(user_id: Optional[int] = None, user_type: Optional[str] = None, db: Session = Depends(get_db)):
    """Lists cases filtered by role and user ID (RBAC)."""
    query = db.query(CaseSubmission)
    if user_type == "citizen" and user_id:
        query = query.filter(CaseSubmission.citizen_id == user_id)
    elif user_type == "lawfirm" and user_id:
        query = query.filter(CaseSubmission.acquired_by_firm_id == user_id)

    cases = query.order_by(CaseSubmission.created_at.desc()).all()
    return [
        {
            "id": c.id,
            "unique_id": c.unique_id,
            "grievance_snippet": c.grievance[:60] + "..." if len(c.grievance) > 60 else c.grievance,
            "user_persona": c.user_persona,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "active_step": c.active_step,
            "win_probability": c.win_probability
        }
        for c in cases
    ]

@app.delete("/api/cases/{case_id}")
def delete_case(case_id: int, db: Session = Depends(get_db)):
    """Deletes a specific case submission dockets folder."""
    case = db.query(CaseSubmission).filter(CaseSubmission.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    case_upload_dir = os.path.join(UPLOAD_DIR, str(case_id))
    if os.path.exists(case_upload_dir):
        shutil.rmtree(case_upload_dir)

    db.delete(case)
    db.commit()
    return {"status": "success", "message": f"Case {case_id} deleted."}
