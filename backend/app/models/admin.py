"""Admin and analytics models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import Intent


class GapEntry(BaseModel):
    """Knowledge gap identified from conversations."""

    id: str
    query: str
    intent: Intent
    occurrences: int = 1
    first_seen: datetime
    last_seen: datetime
    sample_session_ids: list[str] = Field(default_factory=list, max_length=10)
    resolved: bool = False
    resolved_at: datetime | None = None
    resolved_by: str | None = None


class ReindexStatus(BaseModel):
    """Status of knowledge base reindexing."""

    is_running: bool = False
    started_at: datetime | None = None
    completed_at: datetime | None = None
    documents_processed: int = 0
    documents_total: int = 0
    errors: list[str] = Field(default_factory=list)
    last_error: str | None = None


class IntentMetrics(BaseModel):
    """Metrics for a specific intent."""

    intent: Intent
    count: int
    avg_confidence: float
    escalation_rate: float


class TimeSeriesPoint(BaseModel):
    """A single point in time series data."""

    timestamp: datetime
    value: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnalyticsResponse(BaseModel):
    """Analytics dashboard data."""

    period_start: datetime
    period_end: datetime
    total_conversations: int
    total_messages: int
    unique_users: int
    avg_messages_per_session: float
    resolution_rate: float
    escalation_rate: float
    avg_response_time_ms: float
    intent_breakdown: list[IntentMetrics] = Field(default_factory=list)
    satisfaction_score: float | None = None
    top_queries: list[str] = Field(default_factory=list)
    knowledge_gaps: list[GapEntry] = Field(default_factory=list)
