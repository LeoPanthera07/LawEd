import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.escalation import Escalation
from backend.models.lawyer_review import LawyerReview
from backend.models.query import Query
from backend.models.clause_map import ClauseMap
from backend.schemas.escalation import (
    EscalationQueueItem,
    EscalationQueueResponse,
    ReviewEscalationResponse,
)
from backend.schemas.query import ClauseResult


class EscalationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_queue(self) -> EscalationQueueResponse:
        result = await self.db.execute(
            select(Escalation)
            .where(Escalation.status.in_(["pending", "under_review"]))
            .order_by(Escalation.created_at.asc())
        )
        escalations = result.scalars().all()

        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
        reviewed_result = await self.db.execute(
            select(func.count(Escalation.id)).where(
                Escalation.resolved_at >= today_start
            )
        )
        total_reviewed_today = reviewed_result.scalar() or 0

        items = []
        for esc in escalations:
            query_result = await self.db.execute(
                select(Query).where(Query.id == esc.query_id)
            )
            query = query_result.scalar_one_or_none()

            clause_result = await self.db.execute(
                select(ClauseMap).where(ClauseMap.query_id == esc.query_id)
            )
            clause_map = clause_result.scalar_one_or_none()

            items.append(
                EscalationQueueItem(
                    escalation_id=str(esc.id),
                    query_id=str(esc.query_id),
                    reason=esc.reason,
                    confidence_score=float(esc.confidence_score) if esc.confidence_score else None,
                    high_stakes_flag=esc.high_stakes_flag,
                    query_summary=query.input_text[:200] if query else "",
                    ai_clause_count=clause_map.clause_count if clause_map else 0,
                    created_at=esc.created_at.isoformat(),
                    status=esc.status,
                )
            )

        return EscalationQueueResponse(
            escalations=items,
            total_pending=len([e for e in items if e.status == "pending"]),
            total_reviewed_today=total_reviewed_today,
        )

    async def review(
        self,
        escalation_id: str,
        lawyer_id: str,
        resolution: str,
        edited_clauses: Optional[list[ClauseResult]],
        lawyer_notes: Optional[str],
        approved_for_writeup: bool,
    ) -> ReviewEscalationResponse:
        esc = await self.db.get(Escalation, uuid.UUID(escalation_id))
        if not esc:
            from backend.core.exceptions import QueryNotFoundError
            raise QueryNotFoundError()

        now = datetime.now(timezone.utc)

        clause_result = await self.db.execute(
            select(ClauseMap).where(ClauseMap.query_id == esc.query_id)
        )
        clause_map = clause_result.scalar_one_or_none()

        review = LawyerReview(
            escalation_id=esc.id,
            lawyer_id=uuid.UUID(lawyer_id),
            original_clauses=clause_map.clauses if clause_map else [],
            edited_clauses=[c.model_dump() for c in edited_clauses] if edited_clauses else None,
            resolution=resolution,
            notes=lawyer_notes,
        )
        self.db.add(review)

        esc.status = "resolved"
        esc.resolution = resolution
        esc.resolved_at = now
        esc.approved_for_writeup = approved_for_writeup
        esc.lawyer_notes = lawyer_notes

        if clause_map:
            clause_map.is_lawyer_reviewed = True
            clause_map.lawyer_reviewed_by = uuid.UUID(lawyer_id)
            clause_map.lawyer_reviewed_at = now

        await self.db.commit()

        return ReviewEscalationResponse(
            escalation_id=str(esc.id),
            status="resolved",
            resolved_at=now.isoformat(),
        )
