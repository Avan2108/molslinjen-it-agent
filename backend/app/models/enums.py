"""Enumeration definitions for the IT Support Agent."""

from enum import Enum


class Intent(str, Enum):
    """User intent classification."""

    KNOWLEDGE_QUERY = "knowledge_query"
    TICKET_CREATE = "ticket_create"
    TICKET_STATUS = "ticket_status"
    DIAGNOSTICS = "diagnostics"
    ONBOARDING = "onboarding"
    ADMIN = "admin"
    OFF_TOPIC = "off_topic"
    UNCLEAR = "unclear"
    FEEDBACK = "feedback"


class MessageRole(str, Enum):
    """Role of a message in conversation."""

    USER = "user"
    AGENT = "agent"


class TicketStatus(str, Enum):
    """FreshService ticket status."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(int, Enum):
    """FreshService ticket priority levels."""

    URGENT = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class FeedbackRating(str, Enum):
    """User feedback rating."""

    UP = "up"
    DOWN = "down"


class FeedbackReason(str, Enum):
    """Reason for negative feedback."""

    TOO_LONG = "too_long"
    WRONG_ANSWER = "wrong_answer"
    DID_NOT_HELP = "did_not_help"


class Locale(str, Enum):
    """Supported locales."""

    AUTO = "auto"
    EN = "en"
    DA = "da"
    SV = "sv"


class UserRole(str, Enum):
    """User role for authorization."""

    EMPLOYEE = "Employee"
    IT_ADMIN = "ITAdmin"


class TicketSource(int, Enum):
    """FreshService ticket source identifier."""

    AI_CHATBOT = 10  # Custom FreshService source


class TableName(str, Enum):
    """Azure Table Storage table names."""

    CHAT_SESSIONS = "ChatSessions"
    FEEDBACK = "Feedback"
    FAQ_EVENTS = "FAQEvents"
    ADMIN_LOG = "AdminLog"
