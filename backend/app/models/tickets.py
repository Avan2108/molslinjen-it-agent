"""Ticket-related models for FreshService integration."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import TicketPriority, TicketSource, TicketStatus


class TicketNote(BaseModel):
    """A note/comment on a ticket."""

    id: int
    body: str
    created_at: datetime
    user_id: int
    is_private: bool = False


class Ticket(BaseModel):
    """FreshService ticket representation."""

    id: int
    subject: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    requester_id: int
    requester_email: str | None = None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None
    closed_at: datetime | None = None
    source: TicketSource = TicketSource.AI_CHATBOT
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    notes: list[TicketNote] = Field(default_factory=list)


class CreateTicketRequest(BaseModel):
    """Request to create a new ticket."""

    subject: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=10000)
    priority: TicketPriority = TicketPriority.MEDIUM
    custom_fields: dict[str, Any] = Field(default_factory=dict)
    # Session ID for linking conversation context
    session_id: str | None = None
