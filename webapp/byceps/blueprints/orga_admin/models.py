# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from collections import namedtuple

from ..orga.models import OrgaFlag
from ..user.models import User, UserDetail


class Birthday(namedtuple(
        'Birthday',
        ['user'])):

    @classmethod
    def of(cls, user):
        return cls(user)


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
    for user in users:
        yield Birthday.of(user)


def sort_birthdays(birthdays):
    return sorted(birthdays,
                  key=lambda b: (
                    b.user.detail.days_until_next_birthday,
                    -b.user.detail.age))
