from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class GenerateWriteupRequest(BaseModel):
    query_id: str
    payment_id: str
    citizen_name: str = Field(..., min_length=2, max_length=255)
    citizen_contact: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")
    incident_date: Optional[date] = None


class GenerateWriteupResponse(BaseModel):
    writeup_id: str
    status: str
    estimated_seconds: int = 25
