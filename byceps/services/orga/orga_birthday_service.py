"""
byceps.services.orga.orga_birthday_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable, Iterator
from itertools import islice

from sqlalchemy import select

from byceps.database import db
from byceps.services.user import user_service
from byceps.services.user.dbmodels import DbUser, DbUserDetail
from byceps.services.user.models import User

from .dbmodels import DbOrgaFlag
from .models import Birthday


def get_orgas_with_birthday_today() -> set[User]:
    """Return the orgas whose birthday is today."""
    orgas_with_birthdays = _collect_orgas_with_known_birthdays()

    return {
        user for user, birthday in orgas_with_birthdays if birthday.is_today
    }


def collect_orgas_with_next_birthdays(
    *, limit: int | None = None
) -> list[tuple[User, Birthday]]:
    """Return the next birthdays of organizers, sorted by month and day."""
    orgas_with_birthdays = _collect_orgas_with_known_birthdays()

    sorted_orgas = sort_users_by_next_birthday(orgas_with_birthdays)

    if limit is not None:
        sorted_orgas = list(islice(sorted_orgas, limit))

    return sorted_orgas


def _collect_orgas_with_known_birthdays() -> Iterator[tuple[User, Birthday]]:
    """Yield all organizers whose birthday is known."""
    user_ids_and_dates_of_birth = (
        db.session.execute(
            select(DbUser.id, DbUserDetail.date_of_birth)
            .join(DbOrgaFlag)
            .join(DbUserDetail)
            .filter(DbUserDetail.date_of_birth.is_not(None))
        )
        .unique()
        .all()
    )

    user_ids = {user_id for user_id, _ in user_ids_and_dates_of_birth}

    users_by_id = user_service.get_users_indexed_by_id(
        user_ids, include_avatars=True
    )

    for user_id, date_of_birth in user_ids_and_dates_of_birth:
        user = users_by_id[user_id]
        birthday = Birthday(date_of_birth)
        yield user, birthday


def sort_users_by_next_birthday(
    users_and_birthdays: Iterable[tuple[User, Birthday]],
) -> list[tuple[User, Birthday]]:
    return list(
        sorted(
            users_and_birthdays,
            key=lambda user_and_birthday: (
                user_and_birthday[1].days_until_next_birthday,
                -(user_and_birthday[1].age or 0),
            ),
        )
    )
