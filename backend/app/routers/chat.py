"""Chat router — conversation endpoints wired to the Handoff Orchestrator."""

import uuid
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app import store
from app.agents import orchestrator

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    language: str = "en"
    images: list[str] = []


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sources: list = []
    escalate: bool = False


class SummarizeRequest(BaseModel):
    session_id: str
    language: str = "en"


@router.post("", response_model=ChatResponse)
async def send_message(request: ChatRequest) -> ChatResponse:
    """Send a message and get an AI agent response."""
    session_id = request.session_id or str(uuid.uuid4())
    store.record_question(request.message)

    result = orchestrator.process(
        session_id=session_id,
        message=request.message,
        language=request.language,
        images=request.images or [],
    )

    store.add_message(
        session_id=session_id,
        user=request.message,
        assistant=result["answer"],
        sources=result.get("sources", []),
        escalate=result.get("escalate", False),
    )

    return ChatResponse(
        session_id=session_id,
        answer=result["answer"],
        sources=result.get("sources", []),
        escalate=result.get("escalate", False),
    )


@router.post("/summarize")
async def summarize_ticket(request: SummarizeRequest) -> dict:
    """Summarize the conversation into a ticket title + description."""
    return orchestrator.summarize_ticket(request.session_id, request.language)


@router.get("/sessions")
async def list_sessions() -> list[dict]:
    """List all chat sessions (used by admin dashboard)."""
    return store.get_all_conversations()


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> dict:
    """Get a specific chat session with full turn history."""
    history = store.get_history(session_id)
    return {"session_id": session_id, "turns": history}


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> dict:
    """Delete a chat session (no-op for in-memory store)."""
    return {"deleted": session_id}
