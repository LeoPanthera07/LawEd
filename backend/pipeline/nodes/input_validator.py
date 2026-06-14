import re

from backend.pipeline.state import PipelineState


async def input_validator_node(state: PipelineState) -> PipelineState:
    raw = state["raw_input"].strip()
    cleaned = re.sub(r"[<>{}]", "", raw)
    cleaned = re.sub(r"\s+", " ", cleaned)

    state["raw_input"] = cleaned
    return state
