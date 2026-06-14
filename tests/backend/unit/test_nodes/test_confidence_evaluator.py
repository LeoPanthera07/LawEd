import pytest

from backend.pipeline.nodes.confidence_evaluator import confidence_evaluator_node


@pytest.mark.asyncio
async def test_confidence_escalates_on_empty_results():
    state = {"merged_clauses": [], "raw_input": "test query"}
    result = await confidence_evaluator_node(state)
    assert result["confidence_score"] == 0.0
    assert result["routing_decision"] == "escalate"


@pytest.mark.asyncio
async def test_confidence_proceeds_on_good_results():
    state = {
        "merged_clauses": [
            {"relevance_score": 0.8, "act": "BNS", "section_number": "303"},
            {"relevance_score": 0.7, "act": "BNS", "section_number": "304"},
            {"relevance_score": 0.6, "act": "BNSS", "section_number": "173"},
        ],
        "raw_input": "someone stole my wallet",
    }
    result = await confidence_evaluator_node(state)
    assert result["confidence_score"] > 0.45
    assert result["routing_decision"] == "proceed"


@pytest.mark.asyncio
async def test_confidence_escalates_on_high_stakes():
    state = {
        "merged_clauses": [
            {"relevance_score": 0.9, "act": "BNS", "section_number": "103"},
        ],
        "raw_input": "someone committed murder in my neighborhood",
    }
    result = await confidence_evaluator_node(state)
    assert result["routing_decision"] == "escalate"
    assert "murder" in result["high_stakes_flags"]
