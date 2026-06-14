from backend.pipeline.state import PipelineState


async def result_merger_node(state: PipelineState) -> PipelineState:
    qdrant = state.get("qdrant_results", [])
    neo4j = state.get("neo4j_results", [])

    seen = set()
    merged = []

    for result in qdrant:
        key = f"{result.get('act')}-{result.get('section_number')}"
        if key not in seen:
            seen.add(key)
            result["source"] = "qdrant"
            merged.append(result)

    for result in neo4j:
        key = f"{result.get('act')}-{result.get('section_number')}"
        if key not in seen:
            seen.add(key)
            result["source"] = "neo4j"
            merged.append(result)

    merged.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    state["merged_clauses"] = merged[:10]
    state["acts_covered"] = list({c.get("act") for c in merged if c.get("act")})
    return state
