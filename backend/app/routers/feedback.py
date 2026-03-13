"""Feedback router for user feedback collection."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.middleware.auth import get_current_user
from app.models import UserClaims
from app.models.enums import FeedbackRating, FeedbackReason

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackRequest(BaseModel):
    """Request to submit feedback."""

    session_id: str
    message_index: int
    rating: FeedbackRating
    reason: FeedbackReason | None = None
    comment: str | None = None


class FeedbackResponse(BaseModel):
    """Response after submitting feedback."""

    success: bool
    feedback_id: str


@router.post("", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    user: UserClaims = Depends(get_current_user),
) -> FeedbackResponse:
    """Submit feedback for a message."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Feedback submission not yet implemented",
    )


@router.get("/stats")
async def get_feedback_stats(
    user: UserClaims = Depends(get_current_user),
    days: int = 30,
) -> dict:
    """Get feedback statistics (admin only)."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Feedback stats not yet implemented",
    )
