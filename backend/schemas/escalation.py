from typing import Optional

from pydantic import BaseModel, Field

from backend.schemas.query import ClauseResult


class EscalationQueueItem(BaseModel):
    escalation_id: str
    query_id: str
    reason: str
    confidence_score: Optional[float] = None
    high_stakes_flag: Optional[str] = None
    query_summary: str
    ai_clause_count: int
    created_at: str
    status: str


class EscalationQueueResponse(BaseModel):
    escalations: list[EscalationQueueItem]
    total_pending: int
    total_reviewed_today: int


class ReviewEscalationRequest(BaseModel):
    resolution: str
    edited_clauses: Optional[list[ClauseResult]] = None
    lawyer_notes: Optional[str] = Field(None, max_length=500)
    approved_for_writeup: bool = True


class ReviewEscalationResponse(BaseModel):
    escalation_id: str
    status: str
    resolved_at: str
