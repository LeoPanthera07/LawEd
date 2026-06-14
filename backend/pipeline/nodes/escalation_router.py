import structlog

from backend.pipeline.state import PipelineState, PipelineStatus

logger = structlog.get_logger()


async def escalation_router_node(state: PipelineState) -> PipelineState:
    logger.info(
        "case_escalated",
        query_id=state.get("query_id"),
        confidence=state.get("confidence_score"),
        high_stakes=state.get("high_stakes_flags", []),
    )

    reason = "high_stakes" if state.get("high_stakes_flags") else "low_confidence"

    state["status"] = PipelineStatus.ESCALATED
    state["final_output"] = {
        "escalation_reason": reason,
        "confidence_score": state.get("confidence_score"),
        "high_stakes_flags": state.get("high_stakes_flags", []),
        "clauses": state.get("merged_clauses", []),
    }
    return state
