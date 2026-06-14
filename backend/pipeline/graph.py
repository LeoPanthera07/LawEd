import structlog
from langgraph.graph import StateGraph, END

from backend.pipeline.state import PipelineState, PipelineStatus
from backend.pipeline.nodes.input_validator import input_validator_node
from backend.pipeline.nodes.language_detector import language_detector_node
from backend.pipeline.nodes.query_expander import query_expander_node
from backend.pipeline.nodes.qdrant_retriever import qdrant_retriever_node
from backend.pipeline.nodes.neo4j_traverser import neo4j_traverser_node
from backend.pipeline.nodes.result_merger import result_merger_node
from backend.pipeline.nodes.confidence_evaluator import confidence_evaluator_node
from backend.pipeline.nodes.response_synthesiser import response_synthesiser_node
from backend.pipeline.nodes.output_formatter import output_formatter_node
from backend.pipeline.nodes.escalation_router import escalation_router_node

logger = structlog.get_logger()


def route_after_confidence(state: PipelineState) -> str:
    return state.get("routing_decision", "escalate")


def build_pipeline() -> StateGraph:
    workflow = StateGraph(PipelineState)

    workflow.add_node("input_validator", input_validator_node)
    workflow.add_node("language_detector", language_detector_node)
    workflow.add_node("query_expander", query_expander_node)
    workflow.add_node("qdrant_retriever", qdrant_retriever_node)
    workflow.add_node("neo4j_traverser", neo4j_traverser_node)
    workflow.add_node("result_merger", result_merger_node)
    workflow.add_node("confidence_evaluator", confidence_evaluator_node)
    workflow.add_node("response_synthesiser", response_synthesiser_node)
    workflow.add_node("output_formatter", output_formatter_node)
    workflow.add_node("escalation_router", escalation_router_node)

    workflow.set_entry_point("input_validator")

    workflow.add_edge("input_validator", "language_detector")
    workflow.add_edge("language_detector", "query_expander")
    workflow.add_edge("query_expander", "qdrant_retriever")
    workflow.add_edge("qdrant_retriever", "neo4j_traverser")
    workflow.add_edge("neo4j_traverser", "result_merger")
    workflow.add_edge("result_merger", "confidence_evaluator")

    workflow.add_conditional_edges(
        "confidence_evaluator",
        route_after_confidence,
        {
            "proceed": "response_synthesiser",
            "escalate": "escalation_router",
        },
    )

    workflow.add_edge("response_synthesiser", "output_formatter")
    workflow.add_edge("output_formatter", END)
    workflow.add_edge("escalation_router", END)

    return workflow.compile()


_pipeline = None


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = build_pipeline()
    return _pipeline


async def run_pipeline(query_id: str, raw_input: str) -> dict:
    pipeline = get_pipeline()

    initial_state = {
        "query_id": query_id,
        "raw_input": raw_input,
        "errors": [],
        "status": PipelineStatus.PROCESSING,
    }

    config = {"configurable": {"thread_id": query_id}}

    try:
        final_state = await pipeline.ainvoke(initial_state, config=config)
        return final_state
    except Exception as e:
        logger.error("pipeline_failed", query_id=query_id, error=str(e), exc_info=True)
        return {
            "query_id": query_id,
            "status": PipelineStatus.FAILED,
            "errors": [str(e)],
            "final_output": None,
        }
