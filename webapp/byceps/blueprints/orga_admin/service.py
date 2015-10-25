# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..orga.models import Membership, OrgaFlag, OrgaTeam
from ..user.models import User, UserDetail


def get_organizers_for_brand(brand):
    """Return all users flagged as organizers for the brand."""
    return User.query \
        .join(OrgaFlag).filter(OrgaFlag.brand == brand) \
        .options(db.joinedload('detail')) \
        .all()


def get_unassigned_orgas_for_party(party):
    """Return organizers that are not assigned to a team for the party."""
    assigned_orgas = User.query \
        .join(Membership) \
        .join(OrgaTeam) \
        .filter(OrgaTeam.party == party) \
        .options(db.load_only(User.id ))\
        .all()
    assigned_orga_ids = frozenset(user.id for user in assigned_orgas)

    unassigned_orgas = User.query \
        .filter(db.not_(User.id.in_(assigned_orga_ids))) \
        .join(OrgaFlag).filter(OrgaFlag.brand == party.brand) \
        .options(
            db.load_only('screen_name')
        ) \
        .all()
    unassigned_orgas.sort(key=lambda user: user.screen_name.lower())

    return unassigned_orgas


def get_teams_for_party(party):
    """Return orga teams for that party, ordered by title."""
    return OrgaTeam.query \
        .filter_by(party=party) \
        .order_by(OrgaTeam.title) \
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
        .options(db.joinedload('detail')) \
        .all()


def sort_users_by_next_birthday(users):
    return sorted(users,
                  key=lambda user: (
                    user.detail.days_until_next_birthday,
                    -user.detail.age))
