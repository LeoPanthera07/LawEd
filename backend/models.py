from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from backend.database import Base

class CaseSubmission(Base):
    __tablename__ = "case_submissions"

    id = Column(Integer, primary_key=True, index=True)
    grievance = Column(Text, nullable=False)
    location = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    active_step = Column(String(50), default="intake")  # intake, core, courtroom, completed
    user_persona = Column(String(50), default="individual")  # individual, lawfirm
    win_probability = Column(Float, nullable=True)
    judge_verdict = Column(Text, nullable=True)

    # Relationships
    evidence_items = relationship("EvidenceItem", back_populates="case", cascade="all, delete-orphan")
    fact_extraction = relationship("FactExtraction", back_populates="case", uselist=False, cascade="all, delete-orphan")
    legal_references = relationship("LegalReference", back_populates="case", cascade="all, delete-orphan")
    court_debate_logs = relationship("CourtDebateLog", back_populates="case", cascade="all, delete-orphan")
    drafts = relationship("CaseDraft", back_populates="case", cascade="all, delete-orphan")
    review_flags = relationship("ReviewFlag", back_populates="case", cascade="all, delete-orphan")

class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("case_submissions.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(100), nullable=False)
    file_path = Column(String(512), nullable=True)
    extracted_text = Column(Text, nullable=True)
    support_rating = Column(String(50), default="Medium")  # High, Medium, Low, Irrelevant

    case = relationship("CaseSubmission", back_populates="evidence_items")

class FactExtraction(Base):
    __tablename__ = "fact_extractions"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("case_submissions.id"), nullable=False)
    facts_json = Column(Text, nullable=True)     # JSON string of facts
    timeline_json = Column(Text, nullable=True)  # JSON string of events/dates
    parties_json = Column(Text, nullable=True)   # JSON string of parties (Complainant, Accused)
    location = Column(String(100), nullable=True)
    harm = Column(Text, nullable=True)

    case = relationship("CaseSubmission", back_populates="fact_extraction")

class LegalReference(Base):
    __tablename__ = "legal_references"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("case_submissions.id"), nullable=False)
    code_type = Column(String(50), nullable=False)  # BNS, BSA, BNSS
    section_number = Column(String(50), nullable=False)
    section_title = Column(String(255), nullable=False)
    act_title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    punishment = Column(Text, nullable=True)
    procedural_route = Column(Text, nullable=True)

    case = relationship("CaseSubmission", back_populates="legal_references")

class CourtDebateLog(Base):
    __tablename__ = "court_debate_logs"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("case_submissions.id"), nullable=False)
    argument_index = Column(Integer, nullable=False)
    speaker = Column(String(100), nullable=False)  # Plaintiff_Lawyer, Defense_Lawyer, Judge
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    case = relationship("CaseSubmission", back_populates="court_debate_logs")

class CaseDraft(Base):
    __tablename__ = "case_drafts"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("case_submissions.id"), nullable=False)
    draft_type = Column(String(50), nullable=False)  # brief, verdict, strategy_report
    content = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("CaseSubmission", back_populates="drafts")

class ReviewFlag(Base):
    __tablename__ = "review_flags"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("case_submissions.id"), nullable=False)
    flag_type = Column(String(50), default="weak")  # missing_evidence, procedural_hurdle, legal_risk
    flag_title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(50), default="Medium")  # High, Medium, Low

    case = relationship("CaseSubmission", back_populates="review_flags")
