# -*- coding: utf-8 -*-

"""
byceps.blueprints.orga_admin.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from itertools import islice

from ...database import db

from ..brand.models import Brand
from ..orga.models import Membership, OrgaFlag, OrgaTeam
from ..user.models.detail import UserDetail
from ..user.models.user import User


def get_brands_with_person_counts():
    """Yield (brand, person count) pairs."""
    brands = Brand.query.all()

    person_counts_by_brand_id = get_person_count_by_brand_id()

    for brand in brands:
        person_count = person_counts_by_brand_id[brand.id]
        yield brand, person_count


def get_person_count_by_brand_id():
    """Return organizer count (including 0) per brand, indexed by brand ID."""
    return dict(db.session \
        .query(
            Brand.id,
            db.func.count(OrgaFlag.brand_id)
        ) \
        .outerjoin(OrgaFlag) \
        .group_by(Brand.id) \
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
        .options(db.load_only(User.id)) \
        .all()
    assigned_orga_ids = frozenset(user.id for user in assigned_orgas)

    unassigned_orgas_query = User.query

    if assigned_orga_ids:
        unassigned_orgas_query = unassigned_orgas_query \
            .filter(db.not_(User.id.in_(assigned_orga_ids)))

    unassigned_orgas = unassigned_orgas_query \
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


def count_orgas():
    """Return the number of organizers with the organizer flag set."""
    return User.query \
        .join(OrgaFlag) \
        .count()


def count_orgas_for_brand(brand):
    """Return the number of organizers with the organizer flag set for
    that brand.
    """
    return User.query \
        .join(OrgaFlag).filter(OrgaFlag.brand == brand) \
        .count()


def create_orga_flag(brand_id, user_id):
    """Create an orga flag for a user for brand."""
    orga_flag = OrgaFlag(brand_id, user_id)

    db.session.add(orga_flag)
    db.session.commit()

    return orga_flag


def delete_orga_flag(orga_flag):
    """Delete the orga flag."""
    db.session.delete(orga_flag)
    db.session.commit()


def find_orga_flag(brand_id, user_id):
    """Return the orga flag for that brand and user, or `None` if not found."""
    return OrgaFlag.query \
        .filter_by(brand_id=brand_id) \
        .filter_by(user_id=user_id) \
        .first()


def create_orga_team(party, title):
    """Create an orga team for that party."""
    team = OrgaTeam(party, title)

    db.session.add(team)
    db.session.commit()

    return team


def delete_orga_team(team):
    """Delete the orga team."""
    db.session.delete(team)
    db.session.commit()


def find_orga_team(team_id):
    """Return the team with that id, or `None` if not found."""
    return OrgaTeam.query.get(team_id)


def get_orga_teams_for_party(party):
    """Return all orga teams for that party, with memberships."""
    return OrgaTeam.query \
        .options(db.joinedload('memberships')) \
        .filter_by(party=party) \
        .all()


def create_membership(team, user, duties):
    """Assign the user to the team."""
    membership = Membership(team, user)

    if duties:
        membership.duties = duties

    db.session.add(membership)
    db.session.commit()

    return membership


def update_membership(membership, team, duties):
    """Update the membership."""
    membership.orga_team = team
    membership.duties = duties
    db.session.commit()


def delete_membership(membership):
    """Delete the membership."""
    db.session.delete(membership)
    db.session.commit()


def find_membership(membership_id):
    """Return the membership with that id, or `None` if not found."""
    return Membership.query.get(membership_id)
