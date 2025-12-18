"""
byceps.services.authn.session.authn_session_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from babel import Locale

from byceps.services.authn.events import (
    UserLoggedInToAdminEvent,
    UserLoggedInToSiteEvent,
)
from byceps.services.core.events import EventSite
from byceps.services.site.models import Site
from byceps.services.user.log import user_log_domain_service, user_log_service
from byceps.services.user.log.models import UserLogEntry
from byceps.services.user.models.user import (
    User,
    UserID,
    USER_FALLBACK_AVATAR_URL_PATH,
)

from . import authn_session_repository
from .models import CurrentUser


def delete_session_tokens_for_user(user_id: UserID) -> None:
    """Delete all session tokens that belong to the user."""
    authn_session_repository.delete_session_tokens_for_user(user_id)


def delete_all_session_tokens() -> int:
    """Delete all users' session tokens.

    Return the number of records deleted.
    """
    return authn_session_repository.delete_all_session_tokens()


def is_session_valid(user_id: UserID, auth_token: str) -> bool:
    """Return `True` if the client session is valid, `False` if not."""
    if not user_id:
        # User ID must not be empty.
        return False

    if not auth_token:
        # Authentication token must not be empty.
        return False

    return authn_session_repository.is_token_valid_for_user(auth_token, user_id)


def log_in_user_to_admin(
    user: User, ip_address: str | None
) -> tuple[str, UserLoggedInToAdminEvent]:
    """Create a session token and record the log in to administration."""
    db_session_token = authn_session_repository.get_session_token(user.id)

    occurred_at = datetime.utcnow()

    event = UserLoggedInToAdminEvent(
        occurred_at=occurred_at,
        initiator=user,
        user=user,
        ip_address=ip_address,
    )

    log_entry = _build_admin_login_log_entry(event)
    user_log_service.persist_entry(log_entry)

    authn_session_repository.record_recent_login(user.id, occurred_at)

    return db_session_token.token, event


def _build_admin_login_log_entry(
    event: UserLoggedInToAdminEvent,
) -> UserLogEntry:
    """Create a log entry that represents a user login to administration."""
    data = {}

    if event.ip_address:
        data['ip_address'] = event.ip_address

    return user_log_domain_service.build_entry(
        'user-logged-in-to-admin',
        event.user,
        data,
        occurred_at=event.occurred_at,
    )


def log_in_user_to_site(
    user: User, ip_address: str | None, site: Site
) -> tuple[str, UserLoggedInToSiteEvent]:
    """Create a session token and record the log in to a site."""
    db_session_token = authn_session_repository.get_session_token(user.id)

    occurred_at = datetime.utcnow()

    event = UserLoggedInToSiteEvent(
        occurred_at=occurred_at,
        initiator=user,
        user=user,
        ip_address=ip_address,
        site=EventSite.from_site(site),
    )

    log_entry = _build_site_login_log_entry(event)
    user_log_service.persist_entry(log_entry)

    authn_session_repository.record_recent_login(user.id, occurred_at)

    return db_session_token.token, event


def _build_site_login_log_entry(event: UserLoggedInToSiteEvent) -> UserLogEntry:
    """Create a log entry that represents a user login to a site."""
    data: dict[str, str] = {
        'site_id': str(event.site.id),
    }

    if event.ip_address:
        data['ip_address'] = event.ip_address

    return user_log_domain_service.build_entry(
        'user-logged-in-to-site',
        event.user,
        data,
        occurred_at=event.occurred_at,
    )


def find_recent_login(user_id: UserID) -> datetime | None:
    """Return the time of the user's most recent login, if found."""
    return authn_session_repository.find_recent_login(user_id)


def find_recent_logins_for_users(
    user_ids: set[UserID],
) -> dict[UserID, datetime]:
    """Return the time of the users' most recent logins, if found."""
    return authn_session_repository.find_recent_logins_for_users(user_ids)


def find_logins_for_ip_address(
    ip_address: str,
) -> list[tuple[datetime, UserID]]:
    """Return login timestamp and user ID for logins from the given IP
    address.
    """
    return list(authn_session_repository.find_logins_for_ip_address(ip_address))


def delete_login_entries(occurred_before: datetime) -> int:
    """Delete login log entries which occurred before the given date.

    Return the number of deleted log entries.
    """
    return authn_session_repository.delete_login_entries(occurred_before)


ANONYMOUS_USER_ID = UserID(UUID('00000000-0000-0000-0000-000000000000'))


def get_anonymous_current_user(locale: Locale | None) -> CurrentUser:
    """Return an anonymous current user object."""
    return CurrentUser(
        id=ANONYMOUS_USER_ID,
        screen_name=None,
        initialized=True,
        suspended=False,
        deleted=False,
        avatar_url=USER_FALLBACK_AVATAR_URL_PATH,
        locale=locale,
        authenticated=False,
        permissions=frozenset(),
    )


def get_authenticated_current_user(
    user: User,
    locale: Locale | None,
    permissions: frozenset[str],
) -> CurrentUser:
    """Return an authenticated current user object."""
    return CurrentUser(
        id=user.id,
        screen_name=user.screen_name,
        initialized=True,  # Current user has to be initialized.
        suspended=False,  # Current user cannot be suspended.
        deleted=False,  # Current user cannot be deleted.
        avatar_url=user.avatar_url,
        locale=locale,
        authenticated=True,
        permissions=permissions,
    )
