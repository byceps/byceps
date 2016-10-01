# -*- coding: utf-8 -*-

"""
byceps.services.orga_team.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...blueprints.orga.models import OrgaFlag
from ...blueprints.user.models.user import User
from ...database import db

from .models import Membership, OrgaTeam


def create_team(party_id, title_id):
    """Create an orga team for that party."""
    team = OrgaTeam(party_id, title_id)

    db.session.add(team)
    db.session.commit()

    return team


def delete_team(team):
    """Delete the orga team."""
    db.session.delete(team)
    db.session.commit()


def find_team(team_id):
    """Return the team with that id, or `None` if not found."""
    return OrgaTeam.query.get(team_id)


def get_teams_for_party(party):
    """Return orga teams for that party, ordered by title."""
    return OrgaTeam.query \
        .filter_by(party=party) \
        .order_by(OrgaTeam.title) \
        .all()


def get_teams_for_party_with_memberships(party):
    """Return all orga teams for that party, with memberships."""
    return OrgaTeam.query \
        .options(db.joinedload('memberships')) \
        .filter_by(party=party) \
        .all()


def create_membership(team_id, user_id, duties):
    """Assign the user to the team."""
    membership = Membership(team.id, user.id)

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


def find_membership_for_party(user_id, party_id):
    """Return the user's membership in an orga team of that party."""
    return Membership.query \
        .filter_by(user_id=user_id) \
        .for_party_id(party_id) \
        .one_or_none()


def get_memberships_for_party(party_id):
    """Return all orga team memberships for that party."""
    return Membership.query \
        .for_party_id(party_id) \
        .options(
            db.joinedload('orga_team'),
            db.joinedload('user').load_only('id', 'screen_name'),
            db.joinedload('user').joinedload('detail').load_only('first_names', 'last_name'),
            db.joinedload('user').joinedload('orga_team_memberships'),
        ) \
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
