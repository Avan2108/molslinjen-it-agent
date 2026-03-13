"""Chat router for conversation endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.auth import get_current_user
from app.models import ChatRequest, ChatResponse, UserClaims

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    user: UserClaims = Depends(get_current_user),
) -> ChatResponse:
    """Send a message and get agent response."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Chat endpoint not yet implemented",
    )


@router.get("/sessions")
async def list_sessions(
    user: UserClaims = Depends(get_current_user),
    limit: int = 20,
) -> list[dict]:
    """List user's chat sessions."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Sessions listing not yet implemented",
    )


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    user: UserClaims = Depends(get_current_user),
) -> dict:
    """Get a specific chat session with messages."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Session retrieval not yet implemented",
    )


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user: UserClaims = Depends(get_current_user),
) -> dict:
    """Delete a chat session."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Session deletion not yet implemented",
    )
