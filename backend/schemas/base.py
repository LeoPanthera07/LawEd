import uuid
from datetime import datetime, timezone
from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Meta(BaseModel):
    request_id: str = ""
    timestamp: str = ""
    version: str = "1.0"

    def model_post_init(self, __context):
        if not self.request_id:
            self.request_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[dict] = None
    meta: Meta = Meta()


class ErrorDetail(BaseModel):
    code: str
    message: str
    field: Optional[str] = None
