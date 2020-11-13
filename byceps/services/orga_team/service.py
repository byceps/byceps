"""
byceps.services.orga_team.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import dataclasses
from typing import Dict, Optional, Sequence, Set, Tuple

from ...database import db
from ...typing import PartyID, UserID

from ..orga.models import OrgaFlag as DbOrgaFlag
from ..party import service as party_service
from ..user.models.user import User as DbUser
from ..user import service as user_service
from ..user.transfer.models import User

from .models import Membership as DbMembership, OrgaTeam as DbOrgaTeam
from .transfer.models import (
    Member,
    Membership,
    MembershipID,
    OrgaActivity,
    OrgaTeam,
    OrgaTeamID,
    PublicOrga,
)


# -------------------------------------------------------------------- #
# teams


def create_team(party_id: PartyID, title: str) -> OrgaTeam:
    """Create an orga team for that party."""
    team = DbOrgaTeam(party_id, title)

    db.session.add(team)
    db.session.commit()

    return _db_entity_to_team(team)


def delete_team(team_id: OrgaTeamID) -> None:
    """Delete the orga team."""
    db.session.query(DbOrgaTeam) \
        .filter_by(id=team_id) \
        .delete()

    db.session.commit()


def count_teams_for_parties(party_ids: Set[PartyID]) -> Dict[PartyID, int]:
    """Count orga teams for each party."""
    rows = db.session \
        .query(
            DbOrgaTeam.party_id,
            db.func.count(DbOrgaTeam.id)
        ) \
        .filter(DbOrgaTeam.party_id.in_(party_ids)) \
        .group_by(DbOrgaTeam.party_id) \
        .all()

    return dict(rows)


def count_teams_for_party(party_id: PartyID) -> int:
    """Return the number of orga teams for that party."""
    return DbOrgaTeam.query \
        .filter_by(party_id=party_id) \
        .count()


def get_teams_for_party(party_id: PartyID) -> Set[OrgaTeam]:
    """Return orga teams for that party."""
    teams = DbOrgaTeam.query \
        .filter_by(party_id=party_id) \
        .all()

    return {_db_entity_to_team(team) for team in teams}


def find_team(team_id: OrgaTeamID) -> Optional[OrgaTeam]:
    """Return the team with that id, or `None` if not found."""
    team = _find_db_team(team_id)

    if team is None:
        return None

    return _db_entity_to_team(team)


def _find_db_team(team_id: OrgaTeamID) -> Optional[DbOrgaTeam]:
    """Return the team with that id, or `None` if not found."""
    return DbOrgaTeam.query.get(team_id)


def get_teams_and_members_for_party(
    party_id: PartyID,
) -> Sequence[Tuple[OrgaTeam, Set[Member]]]:
    """Return all orga teams and their corresponding memberships for
    that party.
    """

    teams = DbOrgaTeam.query \
        .options(db.joinedload('memberships')) \
        .filter_by(party_id=party_id) \
        .all()

    user_ids = {ms.user_id for team in teams for ms in team.memberships}
    users = user_service.find_users(user_ids, include_avatars=True)
    users_by_id = {user.id: user for user in users}

    def to_member(db_membership: DbMembership) -> Member:
        membership = _db_entity_to_membership(db_membership)
        user = users_by_id[membership.user_id]

        return Member(membership, user)

    return [
        (_db_entity_to_team(team), {to_member(ms) for ms in team.memberships})
        for team in teams
    ]


def _db_entity_to_team(team: DbOrgaTeam) -> OrgaTeam:
    return OrgaTeam(
        team.id,
        team.party_id,
        team.title,
    )


# -------------------------------------------------------------------- #
# memberships


def create_membership(
    team_id: OrgaTeamID, user_id: UserID, duties: str
) -> Membership:
    """Assign the user to the team."""
    membership = DbMembership(team_id, user_id)

    if duties:
        membership.duties = duties

    db.session.add(membership)
    db.session.commit()

    return _db_entity_to_membership(membership)


def update_membership(
    membership_id: MembershipID, team_id: OrgaTeamID, duties: str
) -> None:
    """Update the membership."""
    membership = _find_db_membership(membership_id)
    if membership is None:
        raise ValueError(f"Unknown membership ID '{membership_id}'")

    team = _find_db_team(team_id)
    if team is None:
        raise ValueError(f"Unknown team ID '{team_id}'")

    membership.orga_team = team
    membership.duties = duties
    db.session.commit()


def delete_membership(membership_id: MembershipID) -> None:
    """Delete the membership."""
    db.session.query(DbMembership) \
        .filter_by(id=membership_id) \
        .delete()

    db.session.commit()


def count_memberships_for_party(party_id: PartyID) -> int:
    """Return the number of memberships the party's teams have in total."""
    return DbMembership.query \
        .for_party(party_id) \
        .count()


def find_membership(membership_id: MembershipID) -> Optional[Membership]:
    """Return the membership with that id, or `None` if not found."""
    membership = _find_db_membership(membership_id)

    if membership is None:
        return None

    return _db_entity_to_membership(membership)


def _find_db_membership(membership_id: MembershipID) -> Optional[DbMembership]:
    """Return the membership with that id, or `None` if not found."""
    return DbMembership.query.get(membership_id)


def find_orga_team_for_user_and_party(
    user_id: UserID, party_id: PartyID
) -> Optional[OrgaTeam]:
    """Return the user's membership in an orga team of that party, or
    `None` of user it not part of an orga team for that party.
    """
    return DbOrgaTeam.query \
        .join(DbMembership) \
        .filter(DbMembership.user_id == user_id) \
        .filter(DbOrgaTeam.party_id == party_id) \
        .one_or_none()


def get_orga_activities_for_user(user_id: UserID) -> Set[OrgaActivity]:
    """Return all orga team activities for that user."""
    memberships = DbMembership.query \
        .options(
            db.joinedload('orga_team').joinedload('party'),
        ) \
        .filter_by(user_id=user_id) \
        .all()

    def to_activity(membership: DbMembership) -> OrgaActivity:
        party = party_service._db_entity_to_party(membership.orga_team.party)
        team = _db_entity_to_team(membership.orga_team)

        return OrgaActivity(
            membership.user_id,
            party,
            team,
            membership.duties,
        )

    return {to_activity(ms) for ms in memberships}


def get_public_orgas_for_party(party_id: PartyID) -> Set[PublicOrga]:
    """Return all public orgas for that party."""
    memberships = DbMembership.query \
        .for_party(party_id) \
        .options(
            db.joinedload('orga_team'),
            db.joinedload('user')
                .load_only('id'),
            db.joinedload('user')
                .joinedload('detail')
                .load_only('first_names', 'last_name'),
        ) \
        .all()

    users_by_id = _get_public_orga_users_by_id(memberships)

    def to_orga(membership: DbMembership) -> PublicOrga:
        user = users_by_id[membership.user_id]

        return PublicOrga(
            user,
            membership.user.detail.full_name,
            membership.orga_team.title,
            membership.duties,
        )

    orgas = {to_orga(ms) for ms in memberships}
    orgas = {orga for orga in orgas if not orga.user.deleted}

    return orgas


def _get_public_orga_users_by_id(
    memberships: DbMembership,
) -> Dict[UserID, User]:
    user_ids = {ms.user_id for ms in memberships}

    users = user_service.find_users(user_ids, include_avatars=True)

    # Each of these users is an organizer.
    users = {dataclasses.replace(u, is_orga=True) for u in users}

    return {user.id: user for user in users}


def has_team_memberships(team_id: OrgaTeamID) -> bool:
    """Return `True` if the team has memberships."""
    return db.session \
        .query(
            db.session
                .query(DbMembership)
                .filter(DbMembership.orga_team_id == team_id)
                .exists()
        ) \
        .scalar()


def _db_entity_to_membership(membership: DbMembership) -> Membership:
    return Membership(
        membership.id,
        membership.orga_team_id,
        membership.user_id,
        membership.duties,
    )


# -------------------------------------------------------------------- #
# copying teams and memberships


def copy_teams_and_memberships(
    source_party_id: PartyID, target_party_id: PartyID
) -> int:
    """Copy teams and memberships from one party to another.

    Return the number of teams.
    """
    source_teams_and_members = get_teams_and_members_for_party(source_party_id)

    for source_team, source_members in source_teams_and_members:
        target_team = create_team(target_party_id, source_team.title)
        for source_member in source_members:
            create_membership(
                target_team.id,
                source_member.user.id,
                source_member.membership.duties,
            )

    return len(source_teams_and_members)


# -------------------------------------------------------------------- #
# organizers


def get_unassigned_orgas_for_party(party_id: PartyID) -> Set[User]:
    """Return organizers that are not assigned to a team for the party."""
    party = party_service.get_party(party_id)

    assigned_orgas = DbUser.query \
        .join(DbMembership) \
        .join(DbOrgaTeam) \
        .filter(DbOrgaTeam.party_id == party.id) \
        .options(db.load_only(DbUser.id)) \
        .all()
    assigned_orga_ids = frozenset(user.id for user in assigned_orgas)

    unassigned_orga_ids_query = db.session \
        .query(DbUser.id)

    if assigned_orga_ids:
        unassigned_orga_ids_query = unassigned_orga_ids_query \
            .filter(db.not_(DbUser.id.in_(assigned_orga_ids)))

    unassigned_orga_ids = unassigned_orga_ids_query \
        .filter_by(deleted=False) \
        .join(DbOrgaFlag).filter(DbOrgaFlag.brand_id == party.brand_id) \
        .all()

    return user_service.find_users(unassigned_orga_ids)


def is_orga_for_party(user_id: UserID, party_id: PartyID) -> bool:
    """Return `True` if the user is an organizer (i.e. is member of an
    organizer team) of that party.
    """
    return db.session \
        .query(
            db.session
                .query(DbMembership)
                .filter(DbMembership.user_id == user_id)
                .join(DbOrgaTeam)
                .filter(DbOrgaTeam.party_id == party_id)
                .exists()
        ) \
        .scalar()
