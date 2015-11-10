# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2015 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...database import db

from ..brand.models import Brand
from ..orga.models import Membership, OrgaFlag, OrgaTeam
from ..party.models import Party
from ..user.models import User, UserDetail


def get_brands_with_person_counts():
    """Yield (brand, person count) pairs."""
    brands = Brand.query.all()

    person_counts_by_brand_id = _get_person_counts_by_brand_id()

    for brand in brands:
        person_count = person_counts_by_brand_id.get(brand.id, 0)
        yield brand, person_count


def _get_person_counts_by_brand_id():
    return dict(db.session \
        .query(
            OrgaFlag.brand_id,
            db.func.count(OrgaFlag.brand_id)
        ) \
        .group_by(OrgaFlag.brand_id) \
        .all())


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


def get_parties_with_team_counts():
    """Yield (party, team count) pairs."""
    parties = Party.query.all()

    team_counts_by_party_id = _get_team_counts_by_party_id()

    for party in parties:
        team_count = team_counts_by_party_id.get(party.id, 0)
        yield party, team_count


def _get_team_counts_by_party_id():
    return dict(db.session \
        .query(
            OrgaTeam.party_id,
            db.func.count(OrgaTeam.party_id)
        ) \
        .group_by(OrgaTeam.party_id) \
        .all())


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
