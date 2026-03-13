"""Tickets router — FreshService with in-memory fallback."""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app import store

router = APIRouter(prefix="/tickets", tags=["tickets"])


class CreateTicketRequest(BaseModel):
    session_id: Optional[str] = None
    summary: str
    description: str
    user_name: str
    priority: str = "medium"


@router.post("")
async def create_ticket(request: CreateTicketRequest) -> dict:
    """Create a support ticket (FreshService or in-memory fallback)."""
    ticket = store.create_ticket(
        session_id=request.session_id or "",
        summary=request.summary,
        description=request.description,
        user_name=request.user_name,
    )
    return ticket


@router.get("")
async def list_tickets() -> list[dict]:
    """List all tickets (admin view)."""
    return store.get_all_tickets()


@router.get("/{ticket_id}")
async def get_ticket(ticket_id: str) -> dict:
    """Get a ticket by its INC-XXXX ID."""
    ticket = store.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return ticket
