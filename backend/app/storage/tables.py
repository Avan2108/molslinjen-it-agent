"""Azure Table Storage abstraction layer."""

import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import uuid4

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.data.tables import TableClient, TableServiceClient
from pydantic import BaseModel

from app.models.enums import (
    FeedbackRating,
    FeedbackReason,
    Intent,
    Locale,
    MessageRole,
    TableName,
)

T = TypeVar("T", bound=BaseModel)


class TableStorageClient(ABC, Generic[T]):
    """Base class for Azure Table Storage operations."""

    def __init__(self, connection_string: str, table_name: TableName) -> None:
        """Initialize table client."""
        self._connection_string = connection_string
        self._table_name = table_name.value
        self._service_client: TableServiceClient | None = None
        self._table_client: TableClient | None = None

    @property
    def table_client(self) -> TableClient:
        """Get or create table client."""
        if self._table_client is None:
            self._service_client = TableServiceClient.from_connection_string(
                self._connection_string
            )
            self._table_client = self._service_client.get_table_client(self._table_name)
            # Ensure table exists
            try:
                self._service_client.create_table(self._table_name)
            except ResourceExistsError:
                pass
        return self._table_client

    @abstractmethod
    def _entity_to_model(self, entity: dict[str, Any]) -> T:
        """Convert table entity to Pydantic model."""
        ...

    @abstractmethod
    def _model_to_entity(self, model: T) -> dict[str, Any]:
        """Convert Pydantic model to table entity."""
        ...

    def get(self, partition_key: str, row_key: str) -> T | None:
        """Get entity by keys."""
        try:
            entity = self.table_client.get_entity(partition_key, row_key)
            return self._entity_to_model(dict(entity))
        except ResourceNotFoundError:
            return None

    def upsert(self, model: T, partition_key: str, row_key: str) -> None:
        """Insert or update entity."""
        entity = self._model_to_entity(model)
        entity["PartitionKey"] = partition_key
        entity["RowKey"] = row_key
        self.table_client.upsert_entity(entity)

    def delete(self, partition_key: str, row_key: str) -> bool:
        """Delete entity. Returns True if deleted, False if not found."""
        try:
            self.table_client.delete_entity(partition_key, row_key)
            return True
        except ResourceNotFoundError:
            return False

    def query(
        self,
        filter_expression: str,
        parameters: dict[str, Any] | None = None,
        select: list[str] | None = None,
    ) -> list[T]:
        """Query entities with OData filter."""
        entities = self.table_client.query_entities(
            query_filter=filter_expression,
            parameters=parameters,
            select=select,
        )
        return [self._entity_to_model(dict(e)) for e in entities]


class ChatSessionEntity(BaseModel):
    """Chat session stored in Table Storage."""

    session_id: str
    user_oid: str
    user_email: str
    created_at: datetime
    updated_at: datetime
    locale: Locale
    messages_json: str  # JSON serialized messages
    metadata_json: str  # JSON serialized metadata
    is_escalated: bool = False
    ticket_id: int | None = None


class ChatSessionsTable(TableStorageClient[ChatSessionEntity]):
    """Table storage for chat sessions."""

    def __init__(self, connection_string: str) -> None:
        super().__init__(connection_string, TableName.CHAT_SESSIONS)

    def _entity_to_model(self, entity: dict[str, Any]) -> ChatSessionEntity:
        return ChatSessionEntity(
            session_id=entity["RowKey"],
            user_oid=entity["PartitionKey"],
            user_email=entity.get("user_email", ""),
            created_at=entity.get("created_at", datetime.utcnow()),
            updated_at=entity.get("updated_at", datetime.utcnow()),
            locale=Locale(entity.get("locale", "auto")),
            messages_json=entity.get("messages_json", "[]"),
            metadata_json=entity.get("metadata_json", "{}"),
            is_escalated=entity.get("is_escalated", False),
            ticket_id=entity.get("ticket_id"),
        )

    def _model_to_entity(self, model: ChatSessionEntity) -> dict[str, Any]:
        return {
            "user_email": model.user_email,
            "created_at": model.created_at,
            "updated_at": model.updated_at,
            "locale": model.locale.value,
            "messages_json": model.messages_json,
            "metadata_json": model.metadata_json,
            "is_escalated": model.is_escalated,
            "ticket_id": model.ticket_id,
        }

    def create_session(
        self, user_oid: str, user_email: str, locale: Locale = Locale.AUTO
    ) -> ChatSessionEntity:
        """Create a new chat session."""
        now = datetime.utcnow()
        session = ChatSessionEntity(
            session_id=str(uuid4()),
            user_oid=user_oid,
            user_email=user_email,
            created_at=now,
            updated_at=now,
            locale=locale,
            messages_json="[]",
            metadata_json="{}",
        )
        self.upsert(session, user_oid, session.session_id)
        return session

    def get_session(self, user_oid: str, session_id: str) -> ChatSessionEntity | None:
        """Get session by user and session ID."""
        return self.get(user_oid, session_id)

    def get_user_sessions(
        self, user_oid: str, limit: int = 20
    ) -> list[ChatSessionEntity]:
        """Get recent sessions for a user."""
        sessions = self.query(f"PartitionKey eq '{user_oid}'")
        return sorted(sessions, key=lambda s: s.updated_at, reverse=True)[:limit]


class FeedbackEntity(BaseModel):
    """Feedback stored in Table Storage."""

    feedback_id: str
    session_id: str
    message_index: int
    user_oid: str
    rating: FeedbackRating
    reason: FeedbackReason | None = None
    comment: str | None = None
    created_at: datetime
    query: str
    response: str
    intent: Intent


class FeedbackTable(TableStorageClient[FeedbackEntity]):
    """Table storage for user feedback."""

    def __init__(self, connection_string: str) -> None:
        super().__init__(connection_string, TableName.FEEDBACK)

    def _entity_to_model(self, entity: dict[str, Any]) -> FeedbackEntity:
        reason = entity.get("reason")
        return FeedbackEntity(
            feedback_id=entity["RowKey"],
            session_id=entity["PartitionKey"],
            message_index=entity.get("message_index", 0),
            user_oid=entity.get("user_oid", ""),
            rating=FeedbackRating(entity["rating"]),
            reason=FeedbackReason(reason) if reason else None,
            comment=entity.get("comment"),
            created_at=entity.get("created_at", datetime.utcnow()),
            query=entity.get("query", ""),
            response=entity.get("response", ""),
            intent=Intent(entity.get("intent", "unclear")),
        )

    def _model_to_entity(self, model: FeedbackEntity) -> dict[str, Any]:
        return {
            "message_index": model.message_index,
            "user_oid": model.user_oid,
            "rating": model.rating.value,
            "reason": model.reason.value if model.reason else None,
            "comment": model.comment,
            "created_at": model.created_at,
            "query": model.query,
            "response": model.response,
            "intent": model.intent.value,
        }

    def add_feedback(
        self,
        session_id: str,
        message_index: int,
        user_oid: str,
        rating: FeedbackRating,
        query: str,
        response: str,
        intent: Intent,
        reason: FeedbackReason | None = None,
        comment: str | None = None,
    ) -> FeedbackEntity:
        """Add feedback for a message."""
        feedback = FeedbackEntity(
            feedback_id=str(uuid4()),
            session_id=session_id,
            message_index=message_index,
            user_oid=user_oid,
            rating=rating,
            reason=reason,
            comment=comment,
            created_at=datetime.utcnow(),
            query=query,
            response=response,
            intent=intent,
        )
        self.upsert(feedback, session_id, feedback.feedback_id)
        return feedback


class FAQEventEntity(BaseModel):
    """FAQ interaction event."""

    event_id: str
    faq_id: str
    user_oid: str
    event_type: str  # "view", "helpful", "not_helpful"
    created_at: datetime
    session_id: str | None = None


class FAQEventsTable(TableStorageClient[FAQEventEntity]):
    """Table storage for FAQ interaction events."""

    def __init__(self, connection_string: str) -> None:
        super().__init__(connection_string, TableName.FAQ_EVENTS)

    def _entity_to_model(self, entity: dict[str, Any]) -> FAQEventEntity:
        return FAQEventEntity(
            event_id=entity["RowKey"],
            faq_id=entity["PartitionKey"],
            user_oid=entity.get("user_oid", ""),
            event_type=entity.get("event_type", "view"),
            created_at=entity.get("created_at", datetime.utcnow()),
            session_id=entity.get("session_id"),
        )

    def _model_to_entity(self, model: FAQEventEntity) -> dict[str, Any]:
        return {
            "user_oid": model.user_oid,
            "event_type": model.event_type,
            "created_at": model.created_at,
            "session_id": model.session_id,
        }

    def log_event(
        self,
        faq_id: str,
        user_oid: str,
        event_type: str,
        session_id: str | None = None,
    ) -> FAQEventEntity:
        """Log an FAQ interaction event."""
        event = FAQEventEntity(
            event_id=str(uuid4()),
            faq_id=faq_id,
            user_oid=user_oid,
            event_type=event_type,
            created_at=datetime.utcnow(),
            session_id=session_id,
        )
        self.upsert(event, faq_id, event.event_id)
        return event


class AdminLogEntity(BaseModel):
    """Admin action log entry."""

    log_id: str
    admin_oid: str
    admin_email: str
    action: str
    target_type: str  # "faq", "document", "settings"
    target_id: str | None = None
    details_json: str
    created_at: datetime


class AdminLogTable(TableStorageClient[AdminLogEntity]):
    """Table storage for admin action logs."""

    def __init__(self, connection_string: str) -> None:
        super().__init__(connection_string, TableName.ADMIN_LOG)

    def _entity_to_model(self, entity: dict[str, Any]) -> AdminLogEntity:
        return AdminLogEntity(
            log_id=entity["RowKey"],
            admin_oid=entity["PartitionKey"],
            admin_email=entity.get("admin_email", ""),
            action=entity.get("action", ""),
            target_type=entity.get("target_type", ""),
            target_id=entity.get("target_id"),
            details_json=entity.get("details_json", "{}"),
            created_at=entity.get("created_at", datetime.utcnow()),
        )

    def _model_to_entity(self, model: AdminLogEntity) -> dict[str, Any]:
        return {
            "admin_email": model.admin_email,
            "action": model.action,
            "target_type": model.target_type,
            "target_id": model.target_id,
            "details_json": model.details_json,
            "created_at": model.created_at,
        }

    def log_action(
        self,
        admin_oid: str,
        admin_email: str,
        action: str,
        target_type: str,
        target_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> AdminLogEntity:
        """Log an admin action."""
        log = AdminLogEntity(
            log_id=str(uuid4()),
            admin_oid=admin_oid,
            admin_email=admin_email,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details_json=json.dumps(details or {}),
            created_at=datetime.utcnow(),
        )
        self.upsert(log, admin_oid, log.log_id)
        return log
