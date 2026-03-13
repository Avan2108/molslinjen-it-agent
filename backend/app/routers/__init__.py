"""API routers package."""

from app.routers.admin import router as admin_router
from app.routers.chat import router as chat_router
from app.routers.faqs import router as faqs_router
from app.routers.feedback import router as feedback_router
from app.routers.tickets import router as tickets_router

__all__ = [
    "chat_router",
    "tickets_router",
    "feedback_router",
    "faqs_router",
    "admin_router",
]
