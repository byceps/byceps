# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from collections import namedtuple
from datetime import date

from ...util.datetime import MonthDay

from ..orga.models import OrgaFlag
from ..user.models import User, UserDetail


class Birthday(namedtuple(
        'Birthday',
        ['user', 'is_today'])):

    @classmethod
    def of(cls, user, today):
        date_of_birth = user.detail.date_of_birth

        is_today = MonthDay.of(date_of_birth).matches(today)

        return cls(user, is_today)


def collect_next_orga_birthdays():
    """Return the next birthdays of organizers, sorted by month and day."""
    orgas_with_birthdays = collect_orgas_with_birthdays()
    birthdays = to_birthdays(orgas_with_birthdays)
    return sort_birthdays(birthdays)


def collect_orgas_with_birthdays():
    """Return all organizers whose birthday is known."""
    return User.query \
        .join(OrgaFlag) \
        .join(UserDetail) \
        .filter(UserDetail.date_of_birth != None) \
        .all()


def to_birthdays(users):
    """Create birthday objects from users."""
    today = date.today()
    for user in users:
        yield Birthday.of(user, today)


def sort_birthdays(birthdays):
    return sorted(birthdays,
                  key=lambda b: (
                    b.user.detail.days_until_next_birthday,
                    -b.user.detail.age))
