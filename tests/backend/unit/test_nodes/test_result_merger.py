import pytest

from backend.pipeline.nodes.result_merger import result_merger_node


@pytest.mark.asyncio
async def test_merger_deduplicates():
    state = {
        "qdrant_results": [
            {"act": "BNS", "section_number": "303", "relevance_score": 0.9},
            {"act": "BNS", "section_number": "304", "relevance_score": 0.7},
        ],
        "neo4j_results": [
            {"act": "BNS", "section_number": "303", "relevance_score": 0.8},
            {"act": "BNSS", "section_number": "173", "relevance_score": 0.6},
        ],
    }
    result = await result_merger_node(state)
    section_numbers = [c["section_number"] for c in result["merged_clauses"]]
    assert len(set(zip([c["act"] for c in result["merged_clauses"]], section_numbers))) == len(
        result["merged_clauses"]
    )


@pytest.mark.asyncio
async def test_merger_sorts_by_relevance():
    state = {
        "qdrant_results": [
            {"act": "BNS", "section_number": "1", "relevance_score": 0.5},
            {"act": "BNS", "section_number": "2", "relevance_score": 0.9},
        ],
        "neo4j_results": [],
    }
    result = await result_merger_node(state)
    assert result["merged_clauses"][0]["relevance_score"] == 0.9


@pytest.mark.asyncio
async def test_merger_limits_to_ten():
    state = {
        "qdrant_results": [
            {"act": "BNS", "section_number": str(i), "relevance_score": 0.5}
            for i in range(15)
        ],
        "neo4j_results": [],
    }
    result = await result_merger_node(state)
    assert len(result["merged_clauses"]) <= 10
