import uuid
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.writeup import Writeup
from backend.schemas.writeup import GenerateWriteupResponse


class WriteupService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate(
        self,
        query_id: str,
        payment_id: str,
        citizen_name: str,
        citizen_contact: str,
        incident_date: Optional[date],
        user_id: str,
    ) -> GenerateWriteupResponse:
        from sqlalchemy import select
        from backend.models.clause_map import ClauseMap

        result = await self.db.execute(
            select(ClauseMap).where(ClauseMap.query_id == uuid.UUID(query_id))
        )
        clause_map = result.scalar_one_or_none()

        writeup = Writeup(
            query_id=uuid.UUID(query_id),
            clause_map_id=clause_map.id if clause_map else uuid.uuid4(),
            payment_id=uuid.UUID(payment_id),
            citizen_name=citizen_name,
            citizen_contact=citizen_contact,
            incident_date=incident_date,
            incident_summary="Generated from query",
            status="generating",
            generation_started_at=datetime.now(timezone.utc),
        )
        self.db.add(writeup)
        await self.db.commit()
        await self.db.refresh(writeup)

        return GenerateWriteupResponse(
            writeup_id=str(writeup.id),
            status="generating",
            estimated_seconds=25,
        )
