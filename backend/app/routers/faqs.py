"""FAQs router for frequently asked questions management."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.middleware.auth import get_current_user
from app.models import UserClaims
from app.models.enums import Locale

router = APIRouter(prefix="/faqs", tags=["faqs"])


class FAQ(BaseModel):
    """FAQ entry."""

    id: str
    question: str
    answer: str
    category: str
    locale: Locale
    order: int = 0
    is_active: bool = True


class FAQCreateRequest(BaseModel):
    """Request to create a new FAQ."""

    question: str
    answer: str
    category: str
    locale: Locale = Locale.EN
    order: int = 0


class FAQUpdateRequest(BaseModel):
    """Request to update an FAQ."""

    question: str | None = None
    answer: str | None = None
    category: str | None = None
    locale: Locale | None = None
    order: int | None = None
    is_active: bool | None = None


@router.get("", response_model=list[FAQ])
async def list_faqs(
    locale: Locale = Locale.EN,
    category: str | None = None,
) -> list[FAQ]:
    """List active FAQs for users."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="FAQ listing not yet implemented",
    )


@router.get("/{faq_id}", response_model=FAQ)
async def get_faq(faq_id: str) -> FAQ:
    """Get a specific FAQ."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="FAQ retrieval not yet implemented",
    )


@router.post("", response_model=FAQ)
async def create_faq(
    request: FAQCreateRequest,
    user: UserClaims = Depends(get_current_user),
) -> FAQ:
    """Create a new FAQ (admin only)."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="FAQ creation not yet implemented",
    )


@router.put("/{faq_id}", response_model=FAQ)
async def update_faq(
    faq_id: str,
    request: FAQUpdateRequest,
    user: UserClaims = Depends(get_current_user),
) -> FAQ:
    """Update an FAQ (admin only)."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="FAQ update not yet implemented",
    )


@router.delete("/{faq_id}")
async def delete_faq(
    faq_id: str,
    user: UserClaims = Depends(get_current_user),
) -> dict:
    """Delete an FAQ (admin only)."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="FAQ deletion not yet implemented",
    )


@router.post("/{faq_id}/helpful")
async def mark_faq_helpful(
    faq_id: str,
    helpful: bool,
    user: UserClaims = Depends(get_current_user),
) -> dict:
    """Mark an FAQ as helpful or not."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="FAQ feedback not yet implemented",
    )
