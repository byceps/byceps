"""
byceps.services.user.user_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.sql import Select

from ...database import db, paginate, Pagination
from ...typing import UserID

from .dbmodels.avatar import DbUserAvatar
from .dbmodels.detail import DbUserDetail
from .dbmodels.user import DbUser
from .models.user import (
    User,
    UserDetail,
    UserEmailAddress,
    UserForAdmin,
    UserForAdminDetail,
    UserStateFilter,
)


class UserIdRejected(Exception):
    """Indicate that the given user ID is not accepted.

    Reasons can include the user ID being
    - not well-formed,
    - unknown,
    or the associated account being
    - not yet initialized,
    - suspended,
    - or deleted.
    """


def find_active_user(
    user_id: UserID,
    *,
    include_avatar: bool = False,
) -> Optional[User]:
    """Return the user with that ID if the account is "active", or
    `None` if:
    - the ID is unknown.
    - the account has not been activated, yet.
    - the account is currently suspended.
    - the account is marked as deleted.
    """
    stmt = _get_user_stmt(include_avatar)

    row = db.session.execute(
        stmt.filter(DbUser.initialized == True)  # noqa: E712
        .filter(DbUser.suspended == False)  # noqa: E712
        .filter(DbUser.deleted == False)  # noqa: E712
        .filter(DbUser.id == user_id)
    ).one_or_none()

    if row is None:
        return None

    return _user_row_to_dto(row)


def find_user(
    user_id: UserID,
    *,
    include_avatar: bool = False,
) -> Optional[User]:
    """Return the user with that ID, or `None` if not found.

    Include avatar URL if requested.
    """
    row = db.session.execute(
        _get_user_stmt(include_avatar).filter(DbUser.id == user_id)
    ).one_or_none()

    if row is None:
        return None

    return _user_row_to_dto(row)


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
    if not user_ids:
        return set()

    rows = db.session.execute(
        _get_user_stmt(include_avatars).filter(
            DbUser.id.in_(frozenset(user_ids))
        )
    ).all()

    return {_user_row_to_dto(row) for row in rows}


def _get_user_stmt(include_avatar: bool) -> Select:
    stmt = select(
        DbUser.id,
        DbUser.screen_name,
        DbUser.suspended,
        DbUser.deleted,
        DbUser.locale,
        DbUserAvatar if include_avatar else db.null(),
    )

    if include_avatar:
        stmt = stmt.outerjoin(DbUserAvatar, DbUser.avatar_id == DbUserAvatar.id)

    return stmt


def _user_row_to_dto(
    row: tuple[UserID, str, bool, bool, Optional[str], Optional[DbUserAvatar]]
) -> User:
    user_id, screen_name, suspended, deleted, locale, avatar = row
    avatar_url = avatar.url if (avatar is not None) else None

    return User(
        id=user_id,
        screen_name=screen_name,
        suspended=suspended,
        deleted=deleted,
        locale=locale,
        avatar_url=avatar_url,
    )


def find_user_by_email_address(email_address: str) -> Optional[User]:
    """Return the user with that email address, or `None` if not found."""
    user = db.session.scalars(
        select(DbUser).filter(
            db.func.lower(DbUser.email_address) == email_address.lower()
        )
    ).one_or_none()

    if user is None:
        return None

    return _db_entity_to_user(user)


def find_user_by_screen_name(
    screen_name: str, *, case_insensitive=False
) -> Optional[User]:
    """Return the user with that screen name, or `None` if not found."""
    user = find_db_user_by_screen_name(
        screen_name, case_insensitive=case_insensitive
    )

    if user is None:
        return None

    return _db_entity_to_user(user)


def find_db_user_by_screen_name(
    screen_name: str, *, case_insensitive=False
) -> Optional[DbUser]:
    """Return the user with that screen name, or `None` if not found."""
    stmt = select(DbUser)

    if case_insensitive:
        stmt = stmt.filter(
            db.func.lower(DbUser.screen_name) == screen_name.lower()
        )
    else:
        stmt = stmt.filter_by(screen_name=screen_name)

    return db.session.scalars(stmt).one_or_none()


def find_user_with_details(user_id: UserID) -> Optional[DbUser]:
    """Return the user and its details."""
    return db.session.scalars(
        select(DbUser)
        .options(db.joinedload(DbUser.detail))
        .filter_by(id=user_id)
    ).one_or_none()


def get_db_user(user_id: UserID) -> DbUser:
    """Return the user with that ID, or raise an exception."""
    user = db.session.get(DbUser, user_id)

    if user is None:
        raise ValueError(f"Unknown user ID '{user_id}'")

    return user


def find_user_for_admin(user_id: UserID) -> Optional[UserForAdmin]:
    """Return the user with that ID, or `None` if not found."""
    user = db.session.scalars(
        select(DbUser)
        .options(
            db.joinedload(DbUser.avatar),
            db.joinedload(DbUser.detail).load_only(
                DbUserDetail.first_name, DbUserDetail.last_name
            ),
        )
        .filter_by(id=user_id)
    ).one_or_none()

    if user is None:
        return None

    return _db_entity_to_user_for_admin(user)


def get_user_for_admin(user_id: UserID) -> UserForAdmin:
    """Return the user with that ID, or raise an exception."""
    user = find_user_for_admin(user_id)

    if user is None:
        raise ValueError(f"Unknown user ID '{user_id}'")

    return user


def get_users_for_admin(user_ids: set[UserID]) -> set[UserForAdmin]:
    """Return the users with those IDs."""
    if not user_ids:
        return set()

    users = (
        db.session.scalars(
            select(DbUser)
            .options(
                db.joinedload(DbUser.avatar),
                db.joinedload(DbUser.detail).load_only(
                    DbUserDetail.first_name, DbUserDetail.last_name
                ),
            )
            .filter(DbUser.id.in_(frozenset(user_ids)))
        )
        .unique()
        .all()
    )

    return {_db_entity_to_user_for_admin(user) for user in users}


def _db_entity_to_user(user: DbUser) -> User:
    return User(
        id=user.id,
        screen_name=user.screen_name,
        suspended=user.suspended,
        deleted=user.deleted,
        locale=user.locale,
        avatar_url=None,
    )


def _db_entity_to_user_for_admin(user: DbUser) -> UserForAdmin:
    full_name = user.detail.full_name if user.detail is not None else None
    detail = UserForAdminDetail(full_name=full_name)

    return UserForAdmin(
        id=user.id,
        screen_name=user.screen_name,
        suspended=user.suspended,
        deleted=user.deleted,
        locale=user.locale,
        avatar_url=user.avatar.url if user.avatar else None,
        created_at=user.created_at,
        initialized=user.initialized,
        detail=detail,
    )


def find_screen_name(user_id: UserID) -> Optional[str]:
    """Return the user's screen name, if available."""
    screen_name = db.session.scalar(
        select(DbUser.screen_name).filter_by(id=user_id)
    )

    if screen_name is None:
        return None

    return screen_name


def find_email_address(user_id: UserID) -> Optional[str]:
    """Return the user's e-mail address, if set."""
    return db.session.scalar(select(DbUser.email_address).filter_by(id=user_id))


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
    row = db.session.execute(
        select(
            DbUser.email_address,
            DbUser.email_address_verified,
        ).filter_by(id=user_id)
    ).one_or_none()

    if row is None:
        raise ValueError(f"Unknown user ID '{user_id}'")

    return UserEmailAddress(
        address=row[0],
        verified=row[1],
    )


def get_email_addresses(user_ids: set[UserID]) -> set[tuple[UserID, str]]:
    """Return the users' e-mail addresses."""
    return db.session.execute(
        select(
            DbUser.id,
            DbUser.email_address,
        ).filter(DbUser.id.in_(user_ids))
    ).all()


def get_detail(user_id: UserID) -> UserDetail:
    """Return the user's details."""
    detail = db.session.get(DbUserDetail, user_id)

    if detail is None:
        raise ValueError(f"Unknown user ID '{user_id}'")

    return UserDetail(
        first_name=detail.first_name,
        last_name=detail.last_name,
        date_of_birth=detail.date_of_birth,
        country=detail.country,
        zip_code=detail.zip_code,
        city=detail.city,
        street=detail.street,
        phone_number=detail.phone_number,
        internal_comment=detail.internal_comment,
        extras=detail.extras,
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


def index_users_by_id(users: set[User]) -> dict[UserID, User]:
    """Map the users' IDs to the corresponding user objects."""
    return {user.id: user for user in users}


def is_screen_name_already_assigned(screen_name: str) -> bool:
    """Return `True` if a user with that screen name exists."""
    return _do_users_matching_filter_exist(DbUser.screen_name, screen_name)


def is_email_address_already_assigned(email_address: str) -> bool:
    """Return `True` if a user with that email address exists."""
    return _do_users_matching_filter_exist(DbUser.email_address, email_address)


def _do_users_matching_filter_exist(
    model_attribute: str, search_value: str
) -> bool:
    """Return `True` if any users match the filter.

    Comparison is done case-insensitively.
    """
    return db.session.scalar(
        select(
            select(DbUser)
            .filter(db.func.lower(model_attribute) == search_value.lower())
            .exists()
        )
    )


def get_users_created_since(
    delta: timedelta, limit: Optional[int] = None
) -> list[UserForAdmin]:
    """Return the user accounts created since `delta` ago."""
    filter_starts_at = datetime.utcnow() - delta

    stmt = (
        select(DbUser)
        .options(
            db.joinedload(DbUser.avatar),
            db.joinedload(DbUser.detail).load_only(
                DbUserDetail.first_name, DbUserDetail.last_name
            ),
        )
        .filter(DbUser.created_at >= filter_starts_at)
        .order_by(DbUser.created_at.desc())
    )

    if limit is not None:
        stmt = stmt.limit(limit)

    users = db.session.scalars(stmt).unique().all()

    return [_db_entity_to_user_for_admin(u) for u in users]


def get_users_paginated(
    page: int,
    per_page: int,
    *,
    search_term: Optional[str] = None,
    state_filter: Optional[UserStateFilter] = None,
) -> Pagination:
    """Return the users to show on the specified page, optionally
    filtered by search term or flags.
    """
    stmt = (
        select(DbUser)
        .options(
            db.joinedload(DbUser.detail).load_only(
                DbUserDetail.first_name, DbUserDetail.last_name
            ),
            db.joinedload(DbUser.avatar),
        )
        .order_by(DbUser.created_at.desc())
    )

    stmt = _filter_by_state(stmt, state_filter)

    if search_term:
        stmt = _filter_by_search_term(stmt, search_term)

    return paginate(
        stmt, page, per_page, item_mapper=_db_entity_to_user_for_admin
    )


def _filter_by_state(
    stmt: Select, state_filter: Optional[UserStateFilter] = None
) -> Select:
    if state_filter == UserStateFilter.active:
        return (
            stmt.filter_by(initialized=True)
            .filter_by(suspended=False)
            .filter_by(deleted=False)
        )
    elif state_filter == UserStateFilter.uninitialized:
        return (
            stmt.filter_by(initialized=False)
            .filter_by(suspended=False)
            .filter_by(deleted=False)
        )
    elif state_filter == UserStateFilter.suspended:
        return stmt.filter_by(suspended=True).filter_by(deleted=False)
    elif state_filter == UserStateFilter.deleted:
        return stmt.filter_by(deleted=True)
    else:
        return stmt


def _filter_by_search_term(stmt: Select, search_term: str) -> Select:
    terms = search_term.split(' ')
    clauses = map(_generate_search_clauses_for_term, terms)

    return stmt.join(DbUserDetail).filter(db.and_(*clauses))


def _generate_search_clauses_for_term(search_term: str) -> Select:
    ilike_pattern = f'%{search_term}%'

    return db.or_(
        DbUser.email_address.ilike(ilike_pattern),
        DbUser.screen_name.ilike(ilike_pattern),
        DbUserDetail.first_name.ilike(ilike_pattern),
        DbUserDetail.last_name.ilike(ilike_pattern),
    )
