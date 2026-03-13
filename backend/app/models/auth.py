"""Authentication and authorization models."""

from pydantic import BaseModel, EmailStr

from app.models.enums import UserRole


class UserClaims(BaseModel):
    """User claims extracted from Azure AD token."""

    oid: str  # Object ID (unique user identifier)
    email: EmailStr
    name: str
    preferred_username: str
    roles: list[UserRole] = []
    tenant_id: str
    department: str | None = None
    job_title: str | None = None

    @property
    def is_admin(self) -> bool:
        """Check if user has IT Admin role."""
        return UserRole.IT_ADMIN in self.roles

    @property
    def display_name(self) -> str:
        """Get display name, falling back to email."""
        return self.name or self.preferred_username or self.email
