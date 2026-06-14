from typing import Any

import structlog

from backend.config import settings

logger = structlog.get_logger()


async def traverse_related_clauses(section_ids: list[str]) -> list[dict[str, Any]]:
    if not section_ids:
        return []

    try:
        from neo4j import AsyncGraphDatabase

        driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )

        related = []
        async with driver.session() as session:
            for section_id in section_ids[:5]:
                result = await session.run(
                    """
                    MATCH (source:Clause {id: $section_id})-[r]->(target:Clause)
                    RETURN target.id as id, target.act as act, target.section as section,
                           target.title as title, target.text as text,
                           type(r) as relationship, r.confidence as confidence
                    LIMIT 5
                    """,
                    section_id=section_id,
                )
                async for record in result:
                    related.append(
                        {
                            "act": record["act"],
                            "section_number": record["section"],
                            "section_title": record["title"],
                            "clause_text": record["text"] or "",
                            "relationship": record["relationship"],
                            "relevance_score": record["confidence"] or 0.5,
                        }
                    )

        await driver.close()
        return related
    except Exception as e:
        logger.warning("neo4j_traversal_error", error=str(e))
        return []
