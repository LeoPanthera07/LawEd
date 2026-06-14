from typing import Any

import structlog

from backend.config import settings

logger = structlog.get_logger()


async def get_qdrant_client():
    from qdrant_client import AsyncQdrantClient

    return AsyncQdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        api_key=settings.QDRANT_API_KEY or None,
    )


async def search_clauses(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    try:
        from backend.clients.embedding_client import embed_query

        query_vector = await embed_query(query)
        client = await get_qdrant_client()

        results = await client.search(
            collection_name=settings.QDRANT_COLLECTION,
            query_vector=query_vector,
            limit=top_k,
        )

        clauses = []
        for hit in results:
            payload = hit.payload or {}
            clauses.append(
                {
                    "act": payload.get("act", ""),
                    "section_number": payload.get("section_number", ""),
                    "section_title": payload.get("section_title", ""),
                    "clause_text": payload.get("clause_text", ""),
                    "chapter": payload.get("chapter", ""),
                    "relevance_score": hit.score,
                }
            )

        return clauses
    except Exception as e:
        logger.error("qdrant_search_error", error=str(e))
        return []
