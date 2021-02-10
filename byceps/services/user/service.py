"""
byceps.services.user.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Dict, Optional, Set, Tuple

from ...database import db, Query
from ...typing import PartyID, UserID

from ..orga_team.models import OrgaTeam, Membership as OrgaTeamMembership
from ..user_avatar.models import Avatar, AvatarSelection

from .models.detail import UserDetail as DbUserDetail
from .models.user import User as DbUser
from .transfer.models import User, UserDetail, UserWithDetail


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


def find_active_db_user(user_id: UserID) -> Optional[DbUser]:
    """Return the user with that ID if the account is "active", or
    `None` if:
    - the ID is unknown.
    - the account has not been activated, yet.
    - the account is currently suspended.
    - the account is marked as deleted.
    """
    return DbUser.query \
        .filter_by(initialized=True) \
        .filter_by(suspended=False) \
        .filter_by(deleted=False) \
        .filter_by(id=user_id) \
        .one_or_none()


def find_active_user(
    user_id: UserID,
    *,
    include_avatar: bool = False,
    include_orga_flag_for_party_id: Optional[PartyID] = None,
) -> Optional[User]:
    """Return the user with that ID if the account is "active", or
    `None` if:
    - the ID is unknown.
    - the account has not been activated, yet.
    - the account is currently suspended.
    - the account is marked as deleted.
    """
    query = _get_user_query(include_avatar, include_orga_flag_for_party_id)

    row = query \
        .filter(DbUser.initialized == True) \
        .filter(DbUser.suspended == False) \
        .filter(DbUser.deleted == False) \
        .filter(DbUser.id == user_id) \
        .one_or_none()

    if row is None:
        return None

    return _user_row_to_dto(row)


def find_user(
    user_id: UserID,
    *,
    include_avatar: bool = False,
    include_orga_flag_for_party_id: Optional[PartyID] = None,
) -> Optional[User]:
    """Return the user with that ID, or `None` if not found.

    Include avatar URL if requested.
    """
    row = _get_user_query(include_avatar, include_orga_flag_for_party_id) \
        .filter(DbUser.id == user_id) \
        .one_or_none()

    if row is None:
        return None

    return _user_row_to_dto(row)


def get_user(
    user_id: UserID,
    *,
    include_avatar: bool = False,
    include_orga_flag_for_party_id: Optional[PartyID] = None,
) -> User:
    """Return the user with that ID, or raise an exception.

    Include avatar URL if requested.
    """
    user = find_user(
        user_id,
        include_avatar=include_avatar,
        include_orga_flag_for_party_id=include_orga_flag_for_party_id,
    )

    if user is None:
        raise ValueError(f"Unknown user ID '{user_id}'")

    return user


def find_users(
    user_ids: Set[UserID],
    *,
    include_avatars: bool = False,
    include_orga_flags_for_party_id: Optional[PartyID] = None,
) -> Set[User]:
    """Return the users with those IDs.

    Their respective avatars' URLs are included, if requested.
    """
    if not user_ids:
        return set()

    query = _get_user_query(include_avatars, include_orga_flags_for_party_id)

    rows = query \
        .filter(DbUser.id.in_(frozenset(user_ids))) \
        .all()

    return {_user_row_to_dto(row) for row in rows}


def _get_user_query(
    include_avatar: bool,
    include_orga_flags_for_party_id: Optional[PartyID] = None,
) -> Query:
    orga_flag_expression = db.false()
    if include_orga_flags_for_party_id is not None:
        orga_flag_expression = _get_orga_flag_subquery(
            include_orga_flags_for_party_id)

    query = db.session \
        .query(
            DbUser.id,
            DbUser.screen_name,
            DbUser.suspended,
            DbUser.deleted,
            Avatar if include_avatar else db.null(),
            orga_flag_expression,
        )

    if include_avatar:
        query = query \
            .outerjoin(AvatarSelection, DbUser.avatar_selection) \
            .outerjoin(Avatar)

    return query


def _get_orga_flag_subquery(party_id: PartyID):
    return db.session \
        .query(
            db.func.count(OrgaTeamMembership.id)
        ) \
        .join(OrgaTeam) \
        .filter(OrgaTeam.party_id == party_id) \
        .filter(OrgaTeamMembership.user_id == DbUser.id) \
        .exists()


def _user_row_to_dto(
    row: Tuple[UserID, str, bool, bool, Optional[Avatar], bool]
) -> User:
    user_id, screen_name, suspended, deleted, avatar, is_orga = row
    avatar_url = avatar.url if avatar else None

    return User(
        user_id,
        screen_name,
        suspended,
        deleted,
        avatar_url,
        is_orga,
    )


def find_user_by_email_address(email_address: str) -> Optional[DbUser]:
    """Return the user with that email address, or `None` if not found."""
    return DbUser.query \
        .filter(
            db.func.lower(DbUser.email_address) == email_address.lower()
        ) \
        .one_or_none()


def find_user_by_screen_name(
    screen_name: str, *, case_insensitive=False
) -> Optional[DbUser]:
    """Return the user with that screen name, or `None` if not found."""
    query = DbUser.query

    if case_insensitive:
        query = query.filter(
            db.func.lower(DbUser.screen_name) == screen_name.lower()
        )
    else:
        query = query.filter_by(screen_name=screen_name)

    return query.one_or_none()


def find_user_with_details(user_id: UserID) -> Optional[DbUser]:
    """Return the user and its details."""
    return DbUser.query \
        .options(db.joinedload('detail')) \
        .get(user_id)


def get_db_user(user_id: UserID) -> Optional[DbUser]:
    """Return the user with that ID, or raise an exception."""
    user = DbUser.query.get(user_id)

    if user is None:
        raise ValueError(f"Unknown user ID '{user_id}'")

    return user


def _db_entity_to_user(user: DbUser) -> User:
    avatar_url = None
    is_orga = False  # Information is not available here by design.

    return User(
        user.id,
        user.screen_name,
        user.suspended,
        user.deleted,
        avatar_url,
        is_orga,
    )


def _db_entity_to_user_detail(detail: DbUserDetail) -> UserDetail:
    return UserDetail(
        detail.first_names,
        detail.last_name,
        detail.date_of_birth,
        detail.country,
        detail.zip_code,
        detail.city,
        detail.street,
        detail.phone_number,
        detail.internal_comment,
        detail.extras,
    )


def _db_entity_to_user_with_detail(user: DbUser) -> UserWithDetail:
    user_dto = _db_entity_to_user(user)
    detail_dto = _db_entity_to_user_detail(user.detail)

    return UserWithDetail(
        user_dto.id,
        user_dto.screen_name,
        user_dto.suspended,
        user_dto.deleted,
        user_dto.avatar_url,
        user_dto.is_orga,
        detail_dto,
    )


def find_screen_name(user_id: UserID) -> Optional[str]:
    """Return the user's screen name, if available."""
    screen_name = db.session \
        .query(DbUser.screen_name) \
        .filter_by(id=user_id) \
        .scalar()

    if screen_name is None:
        return None

    return screen_name


def get_email_address(user_id: UserID) -> str:
    """Return the user's e-mail address."""
    email_address = db.session \
        .query(DbUser.email_address) \
        .filter_by(id=user_id) \
        .scalar()

    if email_address is None:
        raise ValueError(
            f"Unknown user ID '{user_id}' or user has no email address"
        )

    return email_address


def get_email_addresses(user_ids: Set[UserID]) -> Set[Tuple[UserID, str]]:
    """Return the users' e-mail addresses."""
    return db.session \
        .query(
            DbUser.id,
            DbUser.email_address,
        ) \
        .filter(DbUser.id.in_(user_ids)) \
        .all()


def get_sort_key_for_screen_name(user: User) -> Tuple[bool, str]:
    """Return a key for sorting by screen name.

    - Orders screen names case-insensitively.
    - Handles absent screen names (i.e. `None`) and places them at the
      end.
    """
    normalized_screen_name = (user.screen_name or '').lower()
    has_screen_name = bool(normalized_screen_name)
    return not has_screen_name, normalized_screen_name


def index_users_by_id(users: Set[User]) -> Dict[UserID, User]:
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
    return db.session \
        .query(
            db.session \
                .query(DbUser) \
                .filter(db.func.lower(model_attribute) == search_value.lower()) \
                .exists()
        ) \
        .scalar()
