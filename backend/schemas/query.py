from typing import Optional

from pydantic import BaseModel, Field


class QuerySubmitRequest(BaseModel):
    input_text: str = Field(..., min_length=20, max_length=5000)
    is_guest: bool = False


class QuerySubmitResponse(BaseModel):
    query_id: str
    status: str
    estimated_seconds: int = 12


class ClauseResult(BaseModel):
    rank: int
    act: str
    section_number: str
    section_title: str
    clause_text: str
    plain_explanation: str
    relevance_context: str
    relevance_score: float
    source: str


class QueryResultResponse(BaseModel):
    query_id: str
    status: str
    detected_language: Optional[str] = None
    confidence_score: Optional[float] = None
    acts_covered: Optional[list[str]] = None
    clause_count: Optional[int] = None
    clauses: Optional[list[ClauseResult]] = None
    disclaimer: Optional[str] = None
    writeup_available: bool = False
    escalation_message: Optional[str] = None
