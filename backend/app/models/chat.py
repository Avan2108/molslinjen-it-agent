"""Chat request and response models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import Intent, Locale, MessageRole


class Source(BaseModel):
    """Knowledge source reference."""

    title: str
    url: str | None = None
    snippet: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class PreFilterResult(BaseModel):
    """Result from pre-filter/triage step."""

    intent: Intent
    confidence: float = Field(ge=0.0, le=1.0)
    detected_locale: Locale = Locale.AUTO
    extracted_entities: dict[str, Any] = Field(default_factory=dict)
    requires_clarification: bool = False
    clarification_prompt: str | None = None


class Message(BaseModel):
    """A single message in the conversation."""

    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sources: list[Source] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    """Request to the chat endpoint."""

    message: str = Field(min_length=1, max_length=4000)
    session_id: str | None = None
    locale: Locale = Locale.AUTO
    context: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    """Response from the chat endpoint."""

    session_id: str
    message: str
    sources: list[Source] = Field(default_factory=list)
    intent: Intent
    confidence: float = Field(ge=0.0, le=1.0)
    requires_action: bool = False
    action_type: str | None = None
    action_data: dict[str, Any] = Field(default_factory=dict)
    locale: Locale = Locale.EN
