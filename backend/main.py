import os
import shutil
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import json

from backend.database import engine, Base, get_db
from backend.models import CaseSubmission, EvidenceItem, FactExtraction, LegalReference, CourtDebateLog, CaseDraft, ReviewFlag
from backend.agents.orchestrator import orchestrate_case_analysis

# Initialize FastAPI application
app = FastAPI(
    title="LawEdAI Serving Gateway",
    description="Intelligent pre-filing legal case builder and court simulation API."
)

# Enable CORS for local development and integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Define directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------------------------------------------------------
# REST API Endpoints
# ---------------------------------------------------------

@app.post("/api/cases")
def create_case(
    grievance: str = Form(...),
    location: Optional[str] = Form(None),
    user_persona: str = Form("individual"),
    db: Session = Depends(get_db)
):
    """Creates a new case submission with a specific persona (individual or lawfirm)."""
    case = CaseSubmission(
        grievance=grievance,
        location=location,
        user_persona=user_persona,
        active_step="intake"
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return {"status": "success", "case_id": case.id, "persona": case.user_persona}

@app.post("/api/cases/{case_id}/evidence")
def upload_evidence(
    case_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Uploads multiple evidence files and saves them to local storage."""
    case = db.query(CaseSubmission).filter(CaseSubmission.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    case_upload_dir = os.path.join(UPLOAD_DIR, str(case_id))
    if not os.path.exists(case_upload_dir):
        os.makedirs(case_upload_dir, exist_ok=True)

    evidence_list = []
    for file in files:
        file_path = os.path.join(case_upload_dir, file.filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Create evidence db entry
        evidence = EvidenceItem(
            case_id=case_id,
            filename=file.filename,
            file_type=file.content_type or "application/octet-stream",
            file_path=file_path,
            support_rating="Medium"  # Default, rated in analysis agent
        )
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        
        evidence_list.append({
            "id": evidence.id,
            "filename": evidence.filename,
            "file_type": evidence.file_type
        })

    return {"status": "success", "uploaded_evidence": evidence_list}

@app.post("/api/cases/{case_id}/analyze")
def analyze_case(
    case_id: int,
    x_groq_api_key: Optional[str] = Header(None),
    x_openai_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Triggers the orchestrator sequence, executing agents. Supports BYOK headers."""
    case = db.query(CaseSubmission).filter(CaseSubmission.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    # Determine LLM configuration if provided
    api_key = None
    provider = "groq"
    if x_groq_api_key:
        api_key = x_groq_api_key
        provider = "groq"
    elif x_openai_api_key:
        api_key = x_openai_api_key
        provider = "openai"

    try:
        results = orchestrate_case_analysis(db, case_id, api_key, provider)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cases/{case_id}/dashboard")
def get_case_dashboard(case_id: int, db: Session = Depends(get_db)):
    """Fetches full processed legal dashboard parameters for a case submission."""
    case = db.query(CaseSubmission).filter(CaseSubmission.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    facts = db.query(FactExtraction).filter(FactExtraction.case_id == case_id).first()
    legal_refs = db.query(LegalReference).filter(LegalReference.case_id == case_id).all()
    evidence = db.query(EvidenceItem).filter(EvidenceItem.case_id == case_id).all()
    flags = db.query(ReviewFlag).filter(ReviewFlag.case_id == case_id).all()
    
    # Retrieve drafts
    brief_draft = db.query(CaseDraft).filter(CaseDraft.case_id == case_id, CaseDraft.draft_type == "brief").first()
    strategy_draft = db.query(CaseDraft).filter(CaseDraft.case_id == case_id, CaseDraft.draft_type == "strategy_report").first()

    dashboard = {
        "case_id": case.id,
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
        "case_brief": brief_draft.content if brief_draft else None,
        "strategy_report": strategy_draft.content if strategy_draft else None,
        "debate_logs": []
    }

    # If law firm, retrieve courtroom logs
    if case.user_persona == "lawfirm":
        debate_logs = db.query(CourtDebateLog).filter(CourtDebateLog.case_id == case_id).order_by(CourtDebateLog.argument_index).all()
        dashboard["debate_logs"] = [
            {
                "speaker": log.speaker,
                "text": log.text,
                "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            }
            for log in debate_logs
        ]

    return dashboard

@app.get("/api/cases")
def list_cases(db: Session = Depends(get_db)):
    """Lists past case history for the sidebar navigator."""
    cases = db.query(CaseSubmission).order_by(CaseSubmission.created_at.desc()).all()
    return [
        {
            "id": c.id,
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
    """Deletes a specific case and any uploaded file directories."""
    case = db.query(CaseSubmission).filter(CaseSubmission.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found.")

    # Remove physical upload files
    case_upload_dir = os.path.join(UPLOAD_DIR, str(case_id))
    if os.path.exists(case_upload_dir):
        shutil.rmtree(case_upload_dir)

    db.delete(case)
    db.commit()
    return {"status": "success", "message": f"Case {case_id} deleted successfully."}

# ---------------------------------------------------------
# Static File Mounting
# ---------------------------------------------------------
# Create frontend directory structures if missing (index.html, index.css, app.js)
FRONTEND_DIR = os.path.join(os.path.dirname(BASE_DIR), "frontend")
if not os.path.exists(FRONTEND_DIR):
    os.makedirs(FRONTEND_DIR, exist_ok=True)
    os.makedirs(os.path.join(FRONTEND_DIR, "assets", "styles"), exist_ok=True)
    os.makedirs(os.path.join(FRONTEND_DIR, "assets", "js"), exist_ok=True)

# Mount static files at root
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
