from enum import Enum
from typing import Any, Optional, TypedDict


class PipelineStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    FAILED = "failed"


class ClauseData(TypedDict, total=False):
    act: str
    section_number: str
    section_title: str
    clause_text: str
    plain_explanation: str
    relevance_context: str
    relevance_score: float
    source: str


class PipelineState(TypedDict, total=False):
    query_id: str
    raw_input: str
    detected_language: str
    translated_input: str
    act_scope: list[str]
    expanded_queries: list[str]
    qdrant_results: list[dict[str, Any]]
    neo4j_results: list[dict[str, Any]]
    merged_clauses: list[ClauseData]
    confidence_score: float
    high_stakes_flags: list[str]
    routing_decision: str
    synthesised_clauses: list[ClauseData]
    final_output: dict[str, Any]
    acts_covered: list[str]
    status: PipelineStatus
    errors: list[str]
