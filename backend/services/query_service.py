import uuid
from datetime import datetime, timezone
from typing import Optional

import structlog
from fastapi import BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import AccessDeniedError, QueryNotFoundError
from backend.models.clause_map import ClauseMap
from backend.models.query import Query
from backend.schemas.query import QueryResultResponse, QuerySubmitResponse

logger = structlog.get_logger()

DISCLAIMER = (
    "This is legal information, not legal advice. "
    "Consult a qualified lawyer for your specific situation."
)


class QueryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def submit(
        self,
        user_id: str,
        input_text: str,
        is_guest: bool,
        ip_address: Optional[str],
        background_tasks: BackgroundTasks,
    ) -> QuerySubmitResponse:
        query = Query(
            user_id=uuid.UUID(user_id),
            input_text=input_text,
            is_guest=is_guest,
            ip_address=ip_address,
            status="processing",
            processing_started_at=datetime.now(timezone.utc),
        )
        self.db.add(query)
        await self.db.commit()
        await self.db.refresh(query)

        background_tasks.add_task(self._run_pipeline, str(query.id), input_text)

        return QuerySubmitResponse(
            query_id=str(query.id),
            status="processing",
            estimated_seconds=12,
        )

    async def _run_pipeline(self, query_id: str, input_text: str):
        from backend.pipeline.graph import run_pipeline
        from backend.db.database import async_session_factory

        async with async_session_factory() as db:
            try:
                result = await run_pipeline(query_id, input_text)

                query = await db.get(Query, uuid.UUID(query_id))
                if not query:
                    return

                if result.get("status") == "escalated":
                    query.status = "escalated"
                elif result.get("errors"):
                    query.status = "failed"
                    query.pipeline_error = "; ".join(result["errors"])
                else:
                    query.status = "completed"
                    clause_map = ClauseMap(
                        query_id=query.id,
                        clauses=result.get("final_output", {}).get("clauses", []),
                        confidence_score=result.get("confidence_score"),
                        acts_covered=result.get("acts_covered", []),
                        clause_count=len(result.get("final_output", {}).get("clauses", [])),
                    )
                    db.add(clause_map)

                query.completed_at = datetime.now(timezone.utc)
                start = query.processing_started_at
                if start:
                    delta = datetime.now(timezone.utc) - start
                    query.processing_duration_ms = int(delta.total_seconds() * 1000)

                await db.commit()
            except Exception as e:
                logger.error("pipeline_background_error", query_id=query_id, error=str(e))
                query = await db.get(Query, uuid.UUID(query_id))
                if query:
                    query.status = "failed"
                    query.pipeline_error = str(e)
                    await db.commit()

    async def get_result(self, query_id: str, user_id: str) -> QueryResultResponse:
        result = await self.db.execute(
            select(Query).where(Query.id == uuid.UUID(query_id))
        )
        query = result.scalar_one_or_none()
        if not query:
            raise QueryNotFoundError()
        if str(query.user_id) != user_id:
            raise AccessDeniedError()

        response = QueryResultResponse(
            query_id=str(query.id),
            status=query.status,
            detected_language=query.input_language,
            disclaimer=DISCLAIMER,
        )

        if query.status == "completed":
            clause_result = await self.db.execute(
                select(ClauseMap).where(ClauseMap.query_id == query.id)
            )
            clause_map = clause_result.scalar_one_or_none()
            if clause_map:
                response.confidence_score = float(clause_map.confidence_score) if clause_map.confidence_score else None
                response.acts_covered = clause_map.acts_covered
                response.clause_count = clause_map.clause_count
                response.clauses = clause_map.clauses
                response.writeup_available = True

        if query.status == "escalated":
            response.escalation_message = (
                "Your situation involves complex legal considerations. "
                "A verified legal expert is reviewing your case. "
                "You will be notified when the review is complete."
            )

        return response
