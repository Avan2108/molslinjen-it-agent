"""Tickets router for FreshService integration."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.auth import get_current_user
from app.models import CreateTicketRequest, Ticket, UserClaims

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=Ticket)
async def create_ticket(
    request: CreateTicketRequest,
    user: UserClaims = Depends(get_current_user),
) -> Ticket:
    """Create a new support ticket."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Ticket creation not yet implemented",
    )


@router.get("", response_model=list[Ticket])
async def list_tickets(
    user: UserClaims = Depends(get_current_user),
    status_filter: str | None = None,
    limit: int = 20,
) -> list[Ticket]:
    """List user's support tickets."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Tickets listing not yet implemented",
    )


@router.get("/{ticket_id}", response_model=Ticket)
async def get_ticket(
    ticket_id: int,
    user: UserClaims = Depends(get_current_user),
) -> Ticket:
    """Get a specific ticket with notes."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Ticket retrieval not yet implemented",
    )


@router.post("/{ticket_id}/notes")
async def add_ticket_note(
    ticket_id: int,
    body: str,
    user: UserClaims = Depends(get_current_user),
) -> dict:
    """Add a note to a ticket."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Ticket note addition not yet implemented",
    )
