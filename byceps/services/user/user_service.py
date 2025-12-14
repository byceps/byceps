"""
byceps.services.user.user_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import timedelta

from babel import Locale

from byceps.database import Pagination
from byceps.services.user.models.user import UserID

from . import user_repository
from .dbmodels.user import DbUser
from .models.user import (
    User,
    UserDetail,
    UserEmailAddress,
    UserFilter,
    UserForAdmin,
    UserForAdminDetail,
    USER_DELETED_AVATAR_URL_PATH,
    USER_FALLBACK_AVATAR_URL_PATH,
)


def do_users_exist() -> bool:
    """Return `True` if any user accounts (i.e. at least one) exists."""
    return user_repository.do_users_exist()


def find_active_user(
    user_id: UserID,
    *,
    include_avatar: bool = False,
) -> User | None:
    """Return the user with that ID if the account is "active", or
    `None` if:
    - the ID is unknown.
    - the account has not been activated, yet.
    - the account is currently suspended.
    - the account is marked as deleted.
    """
    return user_repository.find_active_user(
        user_id, include_avatar=include_avatar
    )


def find_user(
    user_id: UserID,
    *,
    include_avatar: bool = False,
) -> User | None:
    """Return the user with that ID, or `None` if not found.

    Include avatar URL if requested.
    """
    return user_repository.find_user(user_id, include_avatar=include_avatar)


def get_user(user_id: UserID, *, include_avatar: bool = False) -> User:
    """Return the user with that ID, or raise an exception.

    Include avatar URL if requested.
    """
    user = find_user(user_id, include_avatar=include_avatar)

    if user is None:
        raise ValueError(f"Unknown user ID '{user_id}'")

    return user


def get_users(
    user_ids: set[UserID],
    *,
    include_avatars: bool = False,
) -> set[User]:
    """Return the users with those IDs.

    Their respective avatars' URLs are included, if requested.
    """
    return user_repository.get_users(user_ids, include_avatars=include_avatars)


def get_users_indexed_by_id(
    user_ids: set[UserID],
    *,
    include_avatars: bool = False,
) -> dict[UserID, User]:
    """Return the users with those IDs, indexed by ID.

    Their respective avatars' URLs are included, if requested.
    """
    users = get_users(user_ids, include_avatars=include_avatars)
    return {user.id: user for user in users}


def find_user_by_email_address(email_address: str) -> User | None:
    """Return the user with that email address, or `None` if not found."""
    return user_repository.find_user_by_email_address(email_address)


def find_user_by_email_address_md5_hash(md5_hash: str) -> User | None:
    """Return the user with that MD5 hash for their email address, or
    `None` if not found.
    """
    return user_repository.find_user_by_email_address_md5_hash(md5_hash)


def find_user_by_screen_name(screen_name: str) -> User | None:
    """Return the user with that screen name, or `None` if not found.

    Comparison is done case-insensitively.
    """
    return user_repository.find_user_by_screen_name(screen_name)


def find_db_user_by_screen_name(screen_name: str) -> DbUser | None:
    """Return the user with that screen name, or `None` if not found.

    Comparison is done case-insensitively.
    """
    return user_repository.find_db_user_by_screen_name(screen_name)


def find_user_with_details(user_id: UserID) -> DbUser | None:
    """Return the user and its details."""
    return user_repository.find_user_with_details(user_id)


def get_db_user(user_id: UserID) -> DbUser:
    """Return the user with that ID, or raise an exception."""
    return user_repository.get_db_user(user_id)


def find_user_for_admin(user_id: UserID) -> UserForAdmin | None:
    """Return the user with that ID, or `None` if not found."""
    return user_repository.find_user_for_admin(user_id)


def get_user_for_admin(user_id: UserID) -> UserForAdmin:
    """Return the user with that ID, or raise an exception."""
    user = find_user_for_admin(user_id)

    if user is None:
        raise ValueError(f"Unknown user ID '{user_id}'")

    return user


def get_users_for_admin(user_ids: set[UserID]) -> set[UserForAdmin]:
    """Return the users with those IDs."""
    return user_repository.get_users_for_admin(user_ids)


def get_users_for_admin_indexed_by_id(
    user_ids: set[UserID],
) -> dict[UserID, UserForAdmin]:
    """Return the users with those IDs, indexed by ID."""
    users = get_users_for_admin(user_ids)
    return {user.id: user for user in users}


def get_all_users() -> list[User]:
    """Return all users."""
    db_users = user_repository.get_all_users()
    return [_db_entity_to_user(db_user) for db_user in db_users]


def _db_entity_to_user(db_user: DbUser) -> User:
    return User(
        id=db_user.id,
        screen_name=db_user.screen_name,
        initialized=db_user.initialized,
        suspended=db_user.suspended,
        deleted=db_user.deleted,
        avatar_url=USER_FALLBACK_AVATAR_URL_PATH,
    )


def _db_entity_to_user_for_admin(db_user: DbUser) -> UserForAdmin:
    full_name = db_user.detail.full_name if db_user.detail is not None else None

    if db_user.avatar:
        avatar_url = db_user.avatar.url
    elif db_user.deleted:
        avatar_url = USER_DELETED_AVATAR_URL_PATH
    else:
        avatar_url = USER_FALLBACK_AVATAR_URL_PATH

    detail = UserForAdminDetail(full_name=full_name)

    return UserForAdmin(
        id=db_user.id,
        screen_name=db_user.screen_name,
        initialized=db_user.initialized,
        suspended=db_user.suspended,
        deleted=db_user.deleted,
        avatar_url=avatar_url,
        created_at=db_user.created_at,
        detail=detail,
    )


def find_screen_name(user_id: UserID) -> str | None:
    """Return the user's screen name, if available."""
    return user_repository.find_screen_name(user_id)


def find_email_address(user_id: UserID) -> str | None:
    """Return the user's e-mail address, if set."""
    return user_repository.find_email_address(user_id)


def get_email_address(user_id: UserID) -> str:
    """Return the user's e-mail address."""
    email_address = find_email_address(user_id)

    if email_address is None:
        raise ValueError(
            f"Unknown user ID '{user_id}' or user has no email address"
        )

    return email_address


def get_email_address_data(user_id: UserID) -> UserEmailAddress:
    """Return the user's e-mail address data."""
    db_row = user_repository.find_email_address_data(user_id)

    if db_row is None:
        raise ValueError(f"Unknown user ID '{user_id}'")

    return UserEmailAddress(
        address=db_row[0],
        verified=db_row[1],
    )


def get_email_addresses(
    user_ids: set[UserID],
) -> set[tuple[UserID, str | None]]:
    """Return the users' e-mail addresses."""
    return user_repository.get_email_addresses(user_ids)


def find_locale(user_id: UserID) -> Locale | None:
    """Return the user's locale, if set."""
    return user_repository.find_locale(user_id)


def get_detail(user_id: UserID) -> UserDetail:
    """Return the user's details."""
    db_detail = user_repository.get_detail(user_id)

    return UserDetail(
        first_name=db_detail.first_name,
        last_name=db_detail.last_name,
        date_of_birth=db_detail.date_of_birth,
        country=db_detail.country,
        postal_code=db_detail.postal_code,
        city=db_detail.city,
        street=db_detail.street,
        phone_number=db_detail.phone_number,
        internal_comment=db_detail.internal_comment,
        extras=db_detail.extras,
    )


def get_sort_key_for_screen_name(user: User) -> tuple[bool, str]:
    """Return a key for sorting by screen name.

    - Orders screen names case-insensitively.
    - Handles absent screen names (i.e. `None`) and places them at the
      end.
    """
    normalized_screen_name = (user.screen_name or '').lower()
    has_screen_name = bool(normalized_screen_name)
    return not has_screen_name, normalized_screen_name


def is_screen_name_already_assigned(screen_name: str) -> bool:
    """Return `True` if a user with that screen name exists."""
    return user_repository.is_screen_name_already_assigned(screen_name)


def is_email_address_already_assigned(email_address: str) -> bool:
    """Return `True` if a user with that email address exists."""
    return user_repository.is_email_address_already_assigned(email_address)


def get_users_created_since(
    delta: timedelta, limit: int | None = None
) -> list[UserForAdmin]:
    """Return the user accounts created since `delta` ago."""
    return user_repository.get_users_created_since(delta, limit)


def get_users_paginated(
    page: int,
    per_page: int,
    *,
    search_term: str | None = None,
    user_filter: UserFilter | None = None,
) -> Pagination:
    """Return the users to show on the specified page, optionally
    filtered by search term or flags.
    """
    return user_repository.get_users_paginated(
        page, per_page, search_term=search_term, user_filter=user_filter
    )
