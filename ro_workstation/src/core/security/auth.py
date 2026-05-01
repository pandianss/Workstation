from __future__ import annotations

import getpass

from src.application.services.admin_service import AdminService
from src.application.services.session_service import SessionService
from src.core.config.config_loader import get_app_settings
from src.domain.schemas.user import UserAccess


def resolve_current_user() -> UserAccess:
    """Resolve the current workstation user with admin override support."""
    username = getpass.getuser()
    session_service = SessionService()
    admin_service = AdminService()
    settings = get_app_settings()

    if session_service.is_session_active(username, settings.session_timeout_hours):
        return UserAccess(
            username="special_admin",
            role="ADMIN",
            dept="ALL",
            depts=["ALL"],
            name="Special Admin",
        )

    user = admin_service.get_user(username)
    if user:
        return user

    return UserAccess(
        username=username,
        role="GUEST",
        dept="ALL",
        depts=["ALL"],
        name=username,
    )
