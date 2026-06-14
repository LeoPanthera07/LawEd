from backend.config import settings
from backend.pipeline.state import PipelineState

HIGH_STAKES_KEYWORDS = [
    "murder", "death", "kill", "suicide", "rape", "sexual assault",
    "kidnapping", "abduction", "acid attack", "life imprisonment",
    "dowry death", "child abuse",
]


async def confidence_evaluator_node(state: PipelineState) -> PipelineState:
    merged = state.get("merged_clauses", [])

    if not merged:
        state["confidence_score"] = 0.0
        state["routing_decision"] = "escalate"
        return state

    scores = [c.get("relevance_score", 0) for c in merged]
    avg_score = sum(scores) / len(scores) if scores else 0

    clause_count = len(merged)
    count_bonus = min(clause_count / 10, 0.2)

    confidence = min(avg_score + count_bonus, 1.0)
    state["confidence_score"] = round(confidence, 4)

    raw_input = state.get("raw_input", "").lower()
    high_stakes = [kw for kw in HIGH_STAKES_KEYWORDS if kw in raw_input]
    state["high_stakes_flags"] = high_stakes

    if confidence < settings.CONFIDENCE_ESCALATION_THRESHOLD or high_stakes:
        state["routing_decision"] = "escalate"
    else:
        state["routing_decision"] = "proceed"

    return state
