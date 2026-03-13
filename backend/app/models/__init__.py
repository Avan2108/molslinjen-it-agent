"""Models package."""

from app.models.admin import AnalyticsResponse, GapEntry, ReindexStatus
from app.models.auth import UserClaims
from app.models.chat import ChatRequest, ChatResponse, PreFilterResult, Source
from app.models.enums import (
    FeedbackRating,
    FeedbackReason,
    Intent,
    Locale,
    MessageRole,
    TableName,
    TicketPriority,
    TicketSource,
    TicketStatus,
    UserRole,
)
from app.models.tickets import CreateTicketRequest, Ticket, TicketNote

__all__ = [
    # Enums
    "Intent",
    "MessageRole",
    "TicketStatus",
    "TicketPriority",
    "FeedbackRating",
    "FeedbackReason",
    "Locale",
    "UserRole",
    "TicketSource",
    "TableName",
    # Chat
    "ChatRequest",
    "ChatResponse",
    "Source",
    "PreFilterResult",
    # Tickets
    "Ticket",
    "TicketNote",
    "CreateTicketRequest",
    # Admin
    "AnalyticsResponse",
    "GapEntry",
    "ReindexStatus",
    # Auth
    "UserClaims",
]
