"""
byceps.services.orga.birthday_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from itertools import islice
from typing import Iterator, Optional, Sequence

from ...database import db

from ..user_avatar import service as user_avatar_service
from ..user.dbmodels.detail import UserDetail as DbUserDetail
from ..user.dbmodels.user import User as DbUser
from ..user.transfer.models import User, UserID

from .dbmodels import OrgaFlag as DbOrgaFlag
from .transfer.models import Birthday


def get_orgas_with_birthday_today() -> set[User]:
    """Return the orgas whose birthday is today."""
    orgas_with_birthdays = _collect_orgas_with_known_birthdays()

    return {
        user for user, birthday in orgas_with_birthdays if birthday.is_today
    }


def collect_orgas_with_next_birthdays(
    *, limit: Optional[int] = None
) -> Iterator[tuple[User, Birthday]]:
    """Yield the next birthdays of organizers, sorted by month and day."""
    orgas_with_birthdays = _collect_orgas_with_known_birthdays()

    sorted_orgas = sort_users_by_next_birthday(orgas_with_birthdays)

    if limit is not None:
        sorted_orgas = list(islice(sorted_orgas, limit))

    return sorted_orgas


def _collect_orgas_with_known_birthdays() -> Iterator[tuple[User, Birthday]]:
    """Return all organizers whose birthday is known."""
    users = DbUser.query \
        .join(DbOrgaFlag) \
        .join(DbUserDetail) \
        .filter(DbUserDetail.date_of_birth != None) \
        .options(db.joinedload('detail')) \
        .all()

    user_ids = {user.id for user in users}
    avatar_urls_by_user_id = user_avatar_service.get_avatar_urls_for_users(
        user_ids
    )

    for user in users:
        user_dto = _to_user_dto(user, avatar_urls_by_user_id)
        birthday = Birthday(user.detail.date_of_birth)
        yield user_dto, birthday


def _to_user_dto(
    user: DbUser, avatar_urls_by_user_id: dict[UserID, Optional[str]]
) -> User:
    """Create user DTO from database entity."""
    avatar_url = avatar_urls_by_user_id.get(user.id)

    return User(
        user.id,
        user.screen_name,
        user.suspended,
        user.deleted,
        avatar_url,
        is_orga=True,
    )


def sort_users_by_next_birthday(
    users_and_birthdays: Sequence[tuple[User, Birthday]]
) -> Sequence[tuple[User, Birthday]]:
    return sorted(
        users_and_birthdays,
        key=lambda user_and_birthday: (
            user_and_birthday[1].days_until_next_birthday,
            -user_and_birthday[1].age,
        ),
    )
