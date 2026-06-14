import json

from backend.clients.llm_client import get_llm_client
from backend.pipeline.state import PipelineState

SYNTHESIS_PROMPT = """You are a legal intelligence system for Indian citizens. Given the citizen's situation and retrieved legal clauses, generate a structured response.

CRITICAL RULES:
1. ONLY reference clauses that are in the retrieved context below
2. NEVER invent or hallucinate clause numbers or text
3. Explain each clause in simple, plain language

Citizen's situation: {input_text}

Retrieved clauses:
{clauses_context}

Return ONLY valid JSON with this structure:
{{
  "clauses": [
    {{
      "rank": 1,
      "act": "BNS",
      "section_number": "103",
      "section_title": "Punishment for murder",
      "clause_text": "<exact text from retrieved context>",
      "plain_explanation": "<simple explanation>",
      "relevance_context": "<why this applies to the citizen's situation>",
      "relevance_score": 0.95,
      "source": "qdrant"
    }}
  ]
}}"""


async def response_synthesiser_node(state: PipelineState) -> PipelineState:
    llm = get_llm_client()
    merged = state.get("merged_clauses", [])

    clauses_context = "\n\n".join(
        f"[{c.get('act')} Section {c.get('section_number')}] {c.get('section_title', '')}\n{c.get('clause_text', '')}"
        for c in merged
    )

    prompt = SYNTHESIS_PROMPT.format(
        input_text=state.get("translated_input", state["raw_input"])[:2000],
        clauses_context=clauses_context[:4000],
    )

    try:
        response = await llm.complete(prompt, max_tokens=2000)
        data = json.loads(response)
        synthesised = data.get("clauses", [])

        valid_sections = {f"{c.get('act')}-{c.get('section_number')}" for c in merged}
        verified = []
        for clause in synthesised:
            key = f"{clause.get('act')}-{clause.get('section_number')}"
            if key in valid_sections:
                verified.append(clause)

        state["synthesised_clauses"] = verified
    except Exception as e:
        state["synthesised_clauses"] = [
            {
                "rank": i + 1,
                "act": c.get("act", ""),
                "section_number": c.get("section_number", ""),
                "section_title": c.get("section_title", ""),
                "clause_text": c.get("clause_text", ""),
                "plain_explanation": "Unable to generate explanation",
                "relevance_context": "Retrieved based on semantic similarity",
                "relevance_score": c.get("relevance_score", 0),
                "source": c.get("source", "qdrant"),
            }
            for i, c in enumerate(merged)
        ]
        state["errors"] = state.get("errors", []) + [f"Synthesis failed: {e}"]

    return state
