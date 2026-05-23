import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models import CaseSubmission, FactExtraction, LegalReference, EvidenceItem, CourtDebateLog, CaseDraft
from backend.agents.intake_agent import run_intake_agent
from backend.agents.evidence_agent import run_evidence_agent
from backend.agents.legal_agent import run_legal_agent
from backend.agents.review_agent import run_review_agent
from backend.agents.drafting_agent import run_drafting_agent
from backend.agents.orchestrator import orchestrate_case_analysis

# Setup in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_intake_agent_extraction(db_session):
    # 1. Create a test case
    case = CaseSubmission(
        grievance="I bought a phone for Rs 45,000 from an online dealer in Delhi, but they blocked me and scammed me.",
        location="Delhi",
        user_persona="individual"
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    # 2. Run Intake Agent
    result = run_intake_agent(db_session, case.id)
    assert result["status"] == "success"
    assert result["agent"] == "Intake Agent"

    # 3. Assert facts were saved
    facts_entry = db_session.query(FactExtraction).filter(FactExtraction.case_id == case.id).first()
    assert facts_entry is not None
    assert "Delhi" in facts_entry.location
    assert "financial loss" in facts_entry.harm.lower() or "wrongful" in facts_entry.harm.lower()

def test_legal_agent_statutes_matching(db_session):
    # 1. Create cheating case
    case = CaseSubmission(
        grievance="A dealer cheated me by selling a fake antique piece. I paid them on WhatsApp.",
        location="Mumbai",
        user_persona="individual"
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    # Run intake to populate database
    run_intake_agent(db_session, case.id)

    # 2. Run Legal Agent (Statutory RAG)
    result = run_legal_agent(db_session, case.id)
    assert result["status"] == "success"
    assert result["matched_count"] > 0

    # 3. Assert BNS Section 318 (Cheating) and BSA Section 63 (Digital evidence) are mapped
    refs = db_session.query(LegalReference).filter(LegalReference.case_id == case.id).all()
    section_numbers = [r.section_number for r in refs]
    code_types = [r.code_type for r in refs]

    assert "318" in section_numbers  # Cheating is BNS Sec 318
    assert "63" in section_numbers   # WhatsApp/Digital evidence references BSA Sec 63
    assert "BSA" in code_types
    assert "BNS" in code_types

def test_evidence_and_review_agents(db_session):
    # 1. Create case with uploaded evidence
    case = CaseSubmission(
        grievance="My partner stole Rs 100,000 from our joint account without my consent. I have the ledger printout.",
        location="Bangalore",
        user_persona="individual"
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    # Add evidence
    evidence = EvidenceItem(
        case_id=case.id,
        filename="bank_statement.pdf",
        file_type="application/pdf",
        support_rating="Medium"
    )
    db_session.add(evidence)
    db_session.commit()

    # Run intake & legal
    run_intake_agent(db_session, case.id)
    run_legal_agent(db_session, case.id)

    # 2. Run Evidence Agent
    evi_result = run_evidence_agent(db_session, case.id)
    assert evi_result["status"] == "success"

    # 3. Run Review Agent
    rev_result = run_review_agent(db_session, case.id)
    assert rev_result["status"] == "success"

    # Assert draft and flags are updated
    db_session.refresh(evidence)
    assert evidence.support_rating in ["High", "Medium", "Low"]

def test_full_lawfirm_courtroom_orchestration(db_session):
    # 1. Create a law firm case
    case = CaseSubmission(
        grievance="I was defamed by a post on social media that ruined my business reputation in Delhi.",
        location="Delhi",
        user_persona="lawfirm"
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    # Upload evidence item
    evidence = EvidenceItem(
        case_id=case.id,
        filename="screenshot.png",
        file_type="image/png",
        support_rating="Medium"
    )
    db_session.add(evidence)
    db_session.commit()

    # 2. Trigger Full Orchestration sequence
    orch_result = orchestrate_case_analysis(db_session, case.id)
    assert orch_result["status"] == "success"
    assert orch_result["persona"] == "lawfirm"
    
    # Assert all 8 stages were processed
    steps = [s["step"] for s in orch_result["steps"]]
    assert "Intake Extraction" in steps
    assert "Statutory Mapping (RAG)" in steps
    assert "Prosecution Counsel Argument" in steps
    assert "Defense Counsel Objection" in steps
    assert "Adjudicating Judicial Evaluation" in steps

    # 3. Verify courtroom logs exist in DB
    debate_logs = db_session.query(CourtDebateLog).filter(CourtDebateLog.case_id == case.id).all()
    assert len(debate_logs) > 0
    speakers = [log.speaker for log in debate_logs]
    assert "Plaintiff_Lawyer" in speakers
    assert "Defense_Lawyer" in speakers

    # 4. Verify Judge output (Probability and Verdict saved)
    db_session.refresh(case)
    assert case.win_probability is not None
    assert case.win_probability > 0
    assert case.judge_verdict is not None
    
    # Strategy report created
    strategy = db_session.query(CaseDraft).filter(CaseDraft.case_id == case.id, CaseDraft.draft_type == "strategy_report").first()
    assert strategy is not None
    assert "ADVERSARIAL STRENGTH" in strategy.content

def test_individual_win_probability_orchestration(db_session):
    # 1. Create an individual citizen case
    case = CaseSubmission(
        grievance="I transferred Rs. 45,000 to an online dealer named Suresh in Delhi, but they blocked me on WhatsApp immediately.",
        location="Delhi",
        user_persona="individual"
    )
    db_session.add(case)
    db_session.commit()
    db_session.refresh(case)

    # 2. Trigger Full Orchestration sequence
    orch_result = orchestrate_case_analysis(db_session, case.id)
    assert orch_result["status"] == "success"
    assert orch_result["persona"] == "individual"

    # 3. Verify Judge output (Probability and Verdict saved)
    db_session.refresh(case)
    assert case.win_probability is not None
    assert case.win_probability > 0
    assert case.judge_verdict is not None

    # Verify that facts and custom entities were dynamically extracted
    facts_entry = db_session.query(FactExtraction).filter(FactExtraction.case_id == case.id).first()
    assert facts_entry is not None
    assert "Suresh" in facts_entry.parties_json
    assert "Rs. 45,000" in facts_entry.harm

