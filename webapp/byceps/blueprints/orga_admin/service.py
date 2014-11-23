# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

import csv
import io

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


def serialize_to_csv(field_names, rows):
    """Serialize the rows (must be dictionary objects) to CSV."""
    with io.StringIO(newline='') as f:
        writer = csv.DictWriter(f, field_names,
                                dialect=csv.excel,
                                delimiter=';')

        writer.writeheader()
        writer.writerows(rows)

        f.seek(0)
        yield from f
