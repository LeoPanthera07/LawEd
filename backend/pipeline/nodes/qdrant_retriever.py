import structlog

from backend.clients.qdrant_wrapper import search_clauses
from backend.pipeline.state import PipelineState

logger = structlog.get_logger()


async def qdrant_retriever_node(state: PipelineState) -> PipelineState:
    queries = state.get("expanded_queries", [state["raw_input"]])

    all_results = []
    for query in queries:
        try:
            results = await search_clauses(query, top_k=5)
            all_results.extend(results)
        except Exception as e:
            logger.error("qdrant_retrieval_failed", query=query[:100], error=str(e))
            state["errors"] = state.get("errors", []) + [f"Qdrant retrieval failed: {e}"]

    state["qdrant_results"] = all_results
    return state
