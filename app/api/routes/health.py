from fastapi import APIRouter
from app.core.config import get_settings

settings = get_settings()
router   = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {
        "status":   "ok",
        "env":      settings.ENVIRONMENT,
        "version":  "1.0.0",
    }