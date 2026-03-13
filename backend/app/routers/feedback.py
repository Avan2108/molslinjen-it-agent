"""Feedback router — thumbs up/down ratings."""

from fastapi import APIRouter
from pydantic import BaseModel

from app import store

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    session_id: str
    message_id: str
    rating: str  # "up" or "down"


@router.post("")
async def submit_feedback(request: FeedbackRequest) -> dict:
    """Record thumbs-up or thumbs-down feedback for a message."""
    store.record_feedback(request.session_id, request.message_id, request.rating)
    return {"success": True}
