import pytest

from backend.pipeline.nodes.input_validator import input_validator_node


@pytest.mark.asyncio
async def test_input_validator_strips_html():
    state = {"raw_input": "  <script>alert('xss')</script>  My situation is about theft  "}
    result = await input_validator_node(state)
    assert "<" not in result["raw_input"]
    assert ">" not in result["raw_input"]


@pytest.mark.asyncio
async def test_input_validator_normalizes_whitespace():
    state = {"raw_input": "too   many    spaces   here"}
    result = await input_validator_node(state)
    assert "  " not in result["raw_input"]


@pytest.mark.asyncio
async def test_input_validator_preserves_content():
    state = {"raw_input": "Someone stole my phone at the market yesterday"}
    result = await input_validator_node(state)
    assert "stole" in result["raw_input"]
    assert "phone" in result["raw_input"]
