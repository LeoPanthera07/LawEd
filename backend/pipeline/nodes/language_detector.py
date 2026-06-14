import json

from backend.clients.llm_client import get_llm_client
from backend.pipeline.state import PipelineState

DETECTION_PROMPT = """Detect the language of this text and identify which Indian laws may be relevant.

Text: {text}

Return ONLY valid JSON:
{{
  "language": "en" | "hi" | "hinglish",
  "act_scope": ["BNS", "BNSS", "BSA"],
  "translated_text": "<English translation if not already in English, otherwise same text>"
}}"""


async def language_detector_node(state: PipelineState) -> PipelineState:
    llm = get_llm_client()
    prompt = DETECTION_PROMPT.format(text=state["raw_input"][:1000])

    try:
        response = await llm.complete(prompt, max_tokens=300)
        data = json.loads(response)
        state["detected_language"] = data.get("language", "en")
        state["act_scope"] = data.get("act_scope", ["BNS", "BNSS", "BSA"])
        state["translated_input"] = data.get("translated_text", state["raw_input"])
    except Exception as e:
        state["detected_language"] = "en"
        state["act_scope"] = ["BNS", "BNSS", "BSA"]
        state["translated_input"] = state["raw_input"]
        state["errors"] = state.get("errors", []) + [f"Language detection failed: {e}"]

    return state
