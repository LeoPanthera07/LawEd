import structlog

from backend.pipeline.state import PipelineState

logger = structlog.get_logger()


async def neo4j_traverser_node(state: PipelineState) -> PipelineState:
    qdrant_results = state.get("qdrant_results", [])

    # Extract section IDs from qdrant results for graph traversal
    section_ids = []
    for r in qdrant_results:
        act = r.get("act", "")
        section = r.get("section_number", "")
        if act and section:
            section_ids.append(f"{act}-{section}")

    try:
        from backend.clients.neo4j_wrapper import traverse_related_clauses
        related = await traverse_related_clauses(section_ids)
        state["neo4j_results"] = related
    except Exception as e:
        logger.warning("neo4j_traversal_skipped", error=str(e))
        state["neo4j_results"] = []

    return state
