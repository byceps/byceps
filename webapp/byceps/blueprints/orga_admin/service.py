# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
"""

from ..orga.models import OrgaFlag
from ..user.models import User, UserDetail


def get_organizers():
    """Return all users flagged as organizers."""
    return User.query \
        .join(OrgaFlag) \
        .join(UserDetail) \
        .all()


def collect_orgas_with_next_birthdays():
    """Return the next birthdays of organizers, sorted by month and day."""
    orgas_with_birthdays = collect_orgas_with_birthdays()
    return sort_users_by_next_birthday(orgas_with_birthdays)


def collect_orgas_with_birthdays():
    """Return all organizers whose birthday is known."""
    return User.query \
        .join(OrgaFlag) \
        .join(UserDetail) \
        .filter(UserDetail.date_of_birth != None) \
        .all()


def sort_users_by_next_birthday(users):
    return sorted(users,
                  key=lambda user: (
                    user.detail.days_until_next_birthday,
                    -user.detail.age))
