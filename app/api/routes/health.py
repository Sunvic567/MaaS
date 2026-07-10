from fastapi import APIRouter
from app.core.config import get_settings

settings = get_settings()
router   = APIRouter(tags=["health"])


@router.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {
        "status":   "ok",
        "env":      settings.ENVIRONMENT,
        "version":  "1.0.0",
    }
