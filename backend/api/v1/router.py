from fastapi import APIRouter

from backend.api.v1.auth import router as auth_router
from backend.api.v1.query import router as query_router
from backend.api.v1.payments import router as payments_router
from backend.api.v1.writeup import router as writeup_router
from backend.api.v1.escalations import router as escalations_router
from backend.api.v1.admin import router as admin_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(query_router, prefix="/query", tags=["Query"])
api_router.include_router(payments_router, prefix="/payments", tags=["Payments"])
api_router.include_router(writeup_router, prefix="/writeup", tags=["Writeup"])
api_router.include_router(escalations_router, prefix="/escalations", tags=["Escalations"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
