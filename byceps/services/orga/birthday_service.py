# -*- coding: utf-8 -*-

"""
byceps.services.orga.birthday_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from itertools import islice

from ...database import db

from ..user.models.detail import UserDetail
from ..user.models.user import User

from .models import OrgaFlag


def collect_orgas_with_next_birthdays(*, limit=None):
    """Yield the next birthdays of organizers, sorted by month and day."""
    orgas_with_birthdays = collect_orgas_with_birthdays()

    sorted_orgas = sort_users_by_next_birthday(orgas_with_birthdays)

    if limit is not None:
        sorted_orgas = islice(sorted_orgas, limit)

    yield from sorted_orgas


def collect_orgas_with_birthdays():
    """Return all organizers whose birthday is known."""
    return User.query \
        .join(OrgaFlag) \
        .join(UserDetail) \
        .filter(UserDetail.date_of_birth != None) \
        .options(db.joinedload('detail')) \
        .all()


def sort_users_by_next_birthday(users):
    return sorted(users,
                  key=lambda user: (
                    user.detail.days_until_next_birthday,
                    -user.detail.age))
