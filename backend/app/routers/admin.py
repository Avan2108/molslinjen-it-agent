"""Admin router — analytics and conversation logs."""

from fastapi import APIRouter

from app import store

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/analytics")
async def get_analytics() -> dict:
    """Get analytics dashboard data (totals, satisfaction, top questions)."""
    return store.get_stats()


@router.get("/conversations")
async def get_conversations() -> list[dict]:
    """Get all conversation sessions for the admin dashboard."""
    return store.get_all_conversations()
