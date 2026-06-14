import json

from backend.clients.llm_client import get_llm_client
from backend.pipeline.state import PipelineState

EXPANSION_PROMPT = """You are a legal expert. Given this situation described by an Indian citizen, generate 3-5 search queries to find the most relevant clauses from BNS (criminal law), BNSS (criminal procedure), and BSA (evidence law).

Situation: {text}
Acts in scope: {acts}

Return ONLY valid JSON:
{{
  "queries": [
    "search query 1",
    "search query 2",
    "search query 3"
  ]
}}"""


async def query_expander_node(state: PipelineState) -> PipelineState:
    llm = get_llm_client()
    text = state.get("translated_input", state["raw_input"])
    acts = ", ".join(state.get("act_scope", ["BNS", "BNSS", "BSA"]))

    prompt = EXPANSION_PROMPT.format(text=text[:2000], acts=acts)

    try:
        response = await llm.complete(prompt, max_tokens=400)
        data = json.loads(response)
        state["expanded_queries"] = data.get("queries", [text])
    except Exception as e:
        state["expanded_queries"] = [text]
        state["errors"] = state.get("errors", []) + [f"Query expansion failed: {e}"]

    return state
