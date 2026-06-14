from backend.pipeline.state import PipelineState, PipelineStatus


async def output_formatter_node(state: PipelineState) -> PipelineState:
    clauses = state.get("synthesised_clauses", [])

    for i, clause in enumerate(clauses):
        clause["rank"] = i + 1

    state["final_output"] = {
        "clauses": clauses,
        "clause_count": len(clauses),
        "acts_covered": state.get("acts_covered", []),
        "confidence_score": state.get("confidence_score"),
        "detected_language": state.get("detected_language"),
        "disclaimer": (
            "This is legal information, not legal advice. "
            "Consult a qualified lawyer for your specific situation."
        ),
    }
    state["status"] = PipelineStatus.COMPLETED
    return state
