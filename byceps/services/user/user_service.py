"""
byceps.services.user.user_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.sql import Select

from byceps.database import db, paginate, Pagination
from byceps.services.user.models.user import UserID

from .dbmodels.avatar import DbUserAvatar
from .dbmodels.detail import DbUserDetail
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
    return db.session.scalar(select(select(DbUser).exists())) or False


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
    stmt = _get_user_stmt(include_avatar)

    user_row = (
        db.session.execute(
            stmt.filter(DbUser.initialized == True)  # noqa: E712
            .filter(DbUser.suspended == False)  # noqa: E712
            .filter(DbUser.deleted == False)  # noqa: E712
            .filter(DbUser.id == user_id)
        )
        .tuples()
        .one_or_none()
    )

    if user_row is None:
        return None

    return _user_row_to_dto(user_row)


def find_user(
    user_id: UserID,
    *,
    include_avatar: bool = False,
) -> User | None:
    """Return the user with that ID, or `None` if not found.

    Include avatar URL if requested.
    """
    user_row = (
        db.session.execute(
            _get_user_stmt(include_avatar).filter(DbUser.id == user_id)
        )
        .tuples()
        .one_or_none()
    )

    if user_row is None:
        return None

    return _user_row_to_dto(user_row)


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

    user_rows = (
        db.session.execute(
            _get_user_stmt(include_avatars).filter(
                DbUser.id.in_(frozenset(user_ids))
            )
        )
        .tuples()
        .all()
    )

    return {_user_row_to_dto(user_row) for user_row in user_rows}


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


def _get_user_stmt(include_avatar: bool) -> Select:
    stmt = select(
        DbUser.id,
        DbUser.screen_name,
        DbUser.initialized,
        DbUser.suspended,
        DbUser.deleted,
        DbUser.locale,
        DbUserAvatar if include_avatar else db.null(),
    )

    if include_avatar:
        stmt = stmt.outerjoin(DbUserAvatar, DbUser.avatar_id == DbUserAvatar.id)

    return stmt


def _user_row_to_dto(
    user_row: tuple[UserID, str, bool, bool, bool, str | None, DbUserAvatar],
) -> User:
    user_id, screen_name, initialized, suspended, deleted, locale, db_avatar = (
        user_row
    )

    if db_avatar:
        avatar_url = db_avatar.url
    elif deleted:
        avatar_url = USER_DELETED_AVATAR_URL_PATH
    else:
        avatar_url = USER_FALLBACK_AVATAR_URL_PATH

    return User(
        id=user_id,
        screen_name=screen_name,
        initialized=initialized,
        suspended=suspended,
        deleted=deleted,
        locale=locale,
        avatar_url=avatar_url,
    )


def find_user_by_email_address(email_address: str) -> User | None:
    """Return the user with that email address, or `None` if not found."""
    user_row = (
        db.session.execute(
            _get_user_stmt(include_avatar=True).filter(
                db.func.lower(DbUser.email_address) == email_address.lower()
            )
        )
        .tuples()
        .one_or_none()
    )

    if user_row is None:
        return None

    return _user_row_to_dto(user_row)


def find_user_by_email_address_md5_hash(md5_hash: str) -> User | None:
    """Return the user with that MD5 hash for their email address, or
    `None` if not found.
    """
    user_row = (
        db.session.execute(
            _get_user_stmt(include_avatar=True).filter(
                db.func.md5(DbUser.email_address) == md5_hash
            )
        )
        .tuples()
        .one_or_none()
    )

    if user_row is None:
        return None

    return _user_row_to_dto(user_row)


def find_user_by_screen_name(screen_name: str) -> User | None:
    """Return the user with that screen name, or `None` if not found.

    Comparison is done case-insensitively.
    """
    stmt = _get_user_stmt(include_avatar=True).filter(
        db.func.lower(DbUser.screen_name) == screen_name.lower()
    )

    user_row = db.session.execute(stmt).tuples().one_or_none()

    if user_row is None:
        return None

    return _user_row_to_dto(user_row)


def find_db_user_by_screen_name(screen_name: str) -> DbUser | None:
    """Return the user with that screen name, or `None` if not found.

    Comparison is done case-insensitively.
    """
    stmt = select(DbUser).filter(
        db.func.lower(DbUser.screen_name) == screen_name.lower()
    )

    return db.session.scalars(stmt).one_or_none()


def find_user_with_details(user_id: UserID) -> DbUser | None:
    """Return the user and its details."""
    return db.session.scalars(
        select(DbUser)
        .options(db.joinedload(DbUser.detail))
        .filter_by(id=user_id)
    ).one_or_none()


def get_db_user(user_id: UserID) -> DbUser:
    """Return the user with that ID, or raise an exception."""
    db_user = db.session.get(DbUser, user_id)

    if db_user is None:
        raise ValueError(f"Unknown user ID '{user_id}'")

    return db_user


def find_user_for_admin(user_id: UserID) -> UserForAdmin | None:
    """Return the user with that ID, or `None` if not found."""
    db_user = db.session.scalars(
        select(DbUser)
        .options(
            db.joinedload(DbUser.avatar),
            db.joinedload(DbUser.detail).load_only(
                DbUserDetail.first_name, DbUserDetail.last_name
            ),
        )
        .filter_by(id=user_id)
    ).one_or_none()

    if db_user is None:
        return None

    return _db_entity_to_user_for_admin(db_user)


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

    db_users = (
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

    return {_db_entity_to_user_for_admin(db_user) for db_user in db_users}


def get_users_for_admin_indexed_by_id(
    user_ids: set[UserID],
) -> dict[UserID, UserForAdmin]:
    """Return the users with those IDs, indexed by ID."""
    users = get_users_for_admin(user_ids)
    return {user.id: user for user in users}


def get_all_users() -> list[User]:
    """Return all users."""
    db_users = db.session.scalars(select(DbUser)).all()
    return [_db_entity_to_user(db_user) for db_user in db_users]


def _db_entity_to_user(db_user: DbUser) -> User:
    return User(
        id=db_user.id,
        screen_name=db_user.screen_name,
        initialized=db_user.initialized,
        suspended=db_user.suspended,
        deleted=db_user.deleted,
        locale=db_user.locale,
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
        locale=db_user.locale,
        avatar_url=avatar_url,
        created_at=db_user.created_at,
        detail=detail,
    )


def find_screen_name(user_id: UserID) -> str | None:
    """Return the user's screen name, if available."""
    screen_name = db.session.scalar(
        select(DbUser.screen_name).filter_by(id=user_id)
    )

    if screen_name is None:
        return None

    return screen_name


def find_email_address(user_id: UserID) -> str | None:
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


def get_email_addresses(
    user_ids: set[UserID],
) -> set[tuple[UserID, str | None]]:
    """Return the users' e-mail addresses."""
    rows = (
        db.session.execute(
            select(
                DbUser.id,
                DbUser.email_address,
            ).filter(DbUser.id.in_(user_ids))
        )
        .tuples()
        .all()
    )

    return set(rows)


def get_detail(user_id: UserID) -> UserDetail:
    """Return the user's details."""
    db_detail = db.session.get(DbUserDetail, user_id)

    if db_detail is None:
        raise ValueError(f"Unknown user ID '{user_id}'")

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
    return (
        db.session.scalar(
            select(
                select(DbUser)
                .filter(db.func.lower(model_attribute) == search_value.lower())
                .exists()
            )
        )
        or False
    )


def get_users_created_since(
    delta: timedelta, limit: int | None = None
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

    db_users = db.session.scalars(stmt).unique().all()

    return [_db_entity_to_user_for_admin(db_user) for db_user in db_users]


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

    stmt = _filter_users(stmt, user_filter)

    if search_term:
        stmt = _filter_by_search_term(stmt, search_term)

    return paginate(
        stmt, page, per_page, item_mapper=_db_entity_to_user_for_admin
    )


def _filter_users(
    stmt: Select, user_filter: UserFilter | None = None
) -> Select:
    match user_filter:
        case UserFilter.active:
            return (
                stmt.filter_by(initialized=True)
                .filter_by(suspended=False)
                .filter_by(deleted=False)
            )
        case UserFilter.uninitialized:
            return (
                stmt.filter_by(initialized=False)
                .filter_by(suspended=False)
                .filter_by(deleted=False)
            )
        case UserFilter.suspended:
            return stmt.filter_by(suspended=True).filter_by(deleted=False)
        case UserFilter.deleted:
            return stmt.filter_by(deleted=True)
        case _:
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
