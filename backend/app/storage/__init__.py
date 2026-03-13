"""Storage package for Azure Table Storage."""

from app.storage.tables import (
    AdminLogTable,
    ChatSessionsTable,
    FAQEventsTable,
    FeedbackTable,
    TableStorageClient,
)

__all__ = [
    "TableStorageClient",
    "ChatSessionsTable",
    "FeedbackTable",
    "FAQEventsTable",
    "AdminLogTable",
]
