"""
byceps.services.orga_team.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional, Sequence

from ...database import db
from ...typing import PartyID, UserID

from ..orga.models import OrgaFlag
from ..party import service as party_service
from ..user.models.user import User as DbUser

from .models import Membership, MembershipID, OrgaTeam, OrgaTeamID


# -------------------------------------------------------------------- #
# teams


def create_team(party_id: PartyID, title: str) -> OrgaTeam:
    """Create an orga team for that party."""
    team = OrgaTeam(party_id, title)

    db.session.add(team)
    db.session.commit()

    return team


def delete_team(team: OrgaTeam) -> None:
    """Delete the orga team."""
    db.session.delete(team)
    db.session.commit()


def find_team(team_id: OrgaTeamID) -> Optional[OrgaTeam]:
    """Return the team with that id, or `None` if not found."""
    return OrgaTeam.query.get(team_id)


def get_teams_for_party(party_id: PartyID) -> Sequence[OrgaTeam]:
    """Return orga teams for that party, ordered by title."""
    return OrgaTeam.query \
        .filter_by(party_id=party_id) \
        .order_by(OrgaTeam.title) \
        .all()


def get_teams_for_party_with_memberships(party_id: PartyID
                                        ) -> Sequence[OrgaTeam]:
    """Return all orga teams for that party, with memberships."""
    return OrgaTeam.query \
        .options(db.joinedload('memberships')) \
        .filter_by(party_id=party_id) \
        .all()


# -------------------------------------------------------------------- #
# memberships


def create_membership(team_id: OrgaTeamID, user_id: UserID, duties: str
                     ) -> Membership:
    """Assign the user to the team."""
    membership = Membership(team_id, user_id)

    if duties:
        membership.duties = duties

    db.session.add(membership)
    db.session.commit()

    return membership


def update_membership(membership: Membership, team: OrgaTeam, duties: str
                     ) -> None:
    """Update the membership."""
    membership.orga_team = team
    membership.duties = duties
    db.session.commit()


def delete_membership(membership: Membership) -> None:
    """Delete the membership."""
    db.session.delete(membership)
    db.session.commit()


def find_membership(membership_id: MembershipID) -> Optional[Membership]:
    """Return the membership with that id, or `None` if not found."""
    return Membership.query.get(membership_id)


def find_membership_for_party(user_id: UserID, party_id: PartyID
                             ) -> Optional[Membership]:
    """Return the user's membership in an orga team of that party, or
    `None` of user it not part of an orga team for that party.
    """
    return Membership.query \
        .filter_by(user_id=user_id) \
        .for_party(party_id) \
        .one_or_none()


def get_memberships_for_party(party_id: PartyID) -> Sequence[Membership]:
    """Return all orga team memberships for that party."""
    return Membership.query \
        .for_party(party_id) \
        .options(
            db.joinedload('orga_team'),
            db.joinedload('user').load_only('id'),
            db.joinedload('user').joinedload('detail').load_only('first_names', 'last_name'),
        ) \
        .all()


def get_memberships_for_user(user_id: UserID) -> Sequence[Membership]:
    """Return all orga team memberships for that user."""
    return Membership.query \
        .options(
            db.joinedload('orga_team').joinedload('party'),
        ) \
        .filter_by(user_id=user_id) \
        .all()


# -------------------------------------------------------------------- #
# organizers


def get_unassigned_orgas_for_party(party_id: PartyID) -> Sequence[DbUser]:
    """Return organizers that are not assigned to a team for the party."""
    party = party_service.get_party(party_id)

    assigned_orgas = DbUser.query \
        .join(Membership) \
        .join(OrgaTeam) \
        .filter(OrgaTeam.party_id == party.id) \
        .options(db.load_only(DbUser.id)) \
        .all()
    assigned_orga_ids = frozenset(user.id for user in assigned_orgas)

    unassigned_orgas_query = DbUser.query

    if assigned_orga_ids:
        unassigned_orgas_query = unassigned_orgas_query \
            .filter(db.not_(DbUser.id.in_(assigned_orga_ids)))

    unassigned_orgas = unassigned_orgas_query \
        .join(OrgaFlag).filter(OrgaFlag.brand_id == party.brand_id) \
        .options(
            db.load_only('screen_name')
        ) \
        .all()
    unassigned_orgas.sort(key=lambda user: user.screen_name.lower())

    return unassigned_orgas


def is_orga_for_party(user_id: UserID, party_id: PartyID) -> bool:
    """Return `True` if the user is an organizer (i.e. is member of an
    organizer team) of that party.
    """
    return db.session \
        .query(
            db.session
                .query(Membership)
                .filter(Membership.user_id == user_id)
                .join(OrgaTeam)
                .filter(OrgaTeam.party_id == party_id)
                .exists()
        ) \
        .scalar()
