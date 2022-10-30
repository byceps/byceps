"""
byceps.services.orga_team.orga_team_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from itertools import groupby
from typing import Iterable, Optional, Sequence

from sqlalchemy import select

from ...database import db
from ...typing import PartyID, UserID

from ..orga.dbmodels import DbOrgaFlag
from ..party import party_service
from ..party.transfer.models import PartyID
from ..user.dbmodels.detail import DbUserDetail
from ..user.dbmodels.user import DbUser
from ..user import user_service
from ..user.transfer.models import User

from .dbmodels import DbMembership, DbOrgaTeam
from .transfer.models import (
    Member,
    Membership,
    MembershipID,
    OrgaActivity,
    OrgaTeam,
    OrgaTeamID,
    PublicOrga,
    TeamAndDuties,
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


def count_teams_for_parties(party_ids: set[PartyID]) -> dict[PartyID, int]:
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
    return db.session \
        .query(DbOrgaTeam) \
        .filter_by(party_id=party_id) \
        .count()


def get_teams_for_party(party_id: PartyID) -> set[OrgaTeam]:
    """Return orga teams for that party."""
    teams = db.session \
        .query(DbOrgaTeam) \
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
    return db.session.get(DbOrgaTeam, team_id)


def get_teams_and_members_for_party(
    party_id: PartyID,
) -> Sequence[tuple[OrgaTeam, set[Member]]]:
    """Return all orga teams and their corresponding memberships for
    that party.
    """
    teams = db.session \
        .query(DbOrgaTeam) \
        .options(db.joinedload(DbOrgaTeam.memberships)) \
        .filter_by(party_id=party_id) \
        .all()

    user_ids = {ms.user_id for team in teams for ms in team.memberships}
    users = user_service.get_users(user_ids, include_avatars=True)
    users_by_id = user_service.index_users_by_id(users)

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
    team_id: OrgaTeamID, user_id: UserID, duties: Optional[str]
) -> Membership:
    """Assign the user to the team."""
    membership = DbMembership(team_id, user_id, duties=duties)

    db.session.add(membership)
    db.session.commit()

    return _db_entity_to_membership(membership)


def update_membership(
    membership_id: MembershipID, team_id: OrgaTeamID, duties: str
) -> Membership:
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

    return _db_entity_to_membership(membership)


def delete_membership(membership_id: MembershipID) -> None:
    """Delete the membership."""
    db.session.query(DbMembership) \
        .filter_by(id=membership_id) \
        .delete()

    db.session.commit()


def count_memberships_for_party(party_id: PartyID) -> int:
    """Return the number of memberships the party's teams have in total."""
    return db.session \
        .query(DbMembership) \
        .join(DbOrgaTeam) \
        .filter(DbOrgaTeam.party_id == party_id) \
        .count()


def get_memberships_for_party(party_id: PartyID) -> set[Membership]:
    """Return memberships for that party."""
    memberships = db.session \
        .query(DbMembership) \
        .join(DbOrgaTeam) \
        .filter(DbOrgaTeam.party_id == party_id) \
        .all()

    return {_db_entity_to_membership(membership) for membership in memberships}


def find_membership(membership_id: MembershipID) -> Optional[Membership]:
    """Return the membership with that id, or `None` if not found."""
    membership = _find_db_membership(membership_id)

    if membership is None:
        return None

    return _db_entity_to_membership(membership)


def _find_db_membership(membership_id: MembershipID) -> Optional[DbMembership]:
    """Return the membership with that id, or `None` if not found."""
    return db.session.query(DbMembership).get(membership_id)


def get_orga_teams_for_user_and_party(
    user_id: UserID, party_id: PartyID
) -> set[OrgaTeam]:
    """Return the user's memberships in any orga teams of that party."""
    db_orga_teams = db.session.scalars(
        select(DbOrgaTeam)
        .join(DbMembership)
        .filter(DbMembership.user_id == user_id)
        .filter(DbOrgaTeam.party_id == party_id)
    ).all()

    return {_db_entity_to_team(team) for team in db_orga_teams}


def get_orga_activities_for_user(user_id: UserID) -> set[OrgaActivity]:
    """Return all orga team activities for that user."""
    memberships = db.session.scalars(
        select(DbMembership)
        .options(db.joinedload(DbMembership.orga_team))
        .filter_by(user_id=user_id)
    ).all()

    party_ids = {ms.orga_team.party_id for ms in memberships}
    parties = party_service.get_parties(party_ids)
    parties_by_id = {party.id: party for party in parties}

    def to_activity(
        user_id: UserID, party_id: PartyID, memberships: Iterable[DbMembership]
    ) -> OrgaActivity:
        return OrgaActivity(
            user_id=user_id,
            party=parties_by_id[party_id],
            teams_and_duties=to_teams_and_duties(memberships),
        )

    def to_teams_and_duties(
        memberships: Iterable[DbMembership],
    ) -> frozenset[TeamAndDuties]:
        return frozenset(
            TeamAndDuties(
                team_title=ms.orga_team.title,
                duties=ms.duties,
            )
            for ms in memberships
        )

    def get_user_and_party(ms: DbMembership) -> tuple[UserID, PartyID]:
        return ms.user_id, ms.orga_team.party_id

    return {
        to_activity(user_id, party_id, ms)
        for (user_id, party_id), ms in groupby(
            sorted(memberships, key=get_user_and_party), key=get_user_and_party
        )
    }


def get_public_orgas_for_party(party_id: PartyID) -> set[PublicOrga]:
    """Return all public orgas for that party."""
    memberships = db.session \
        .query(DbMembership) \
        .join(DbOrgaTeam) \
        .filter(DbOrgaTeam.party_id == party_id) \
        .options(
            db.joinedload(DbMembership.orga_team),
            db.joinedload(DbMembership.user)
                .load_only(DbUser.id),
            db.joinedload(DbMembership.user)
                .joinedload(DbUser.detail)
                .load_only(DbUserDetail.first_name, DbUserDetail.last_name),
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
) -> dict[UserID, User]:
    user_ids = {ms.user_id for ms in memberships}
    users = user_service.get_users(user_ids, include_avatars=True)
    return user_service.index_users_by_id(users)


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


def get_unassigned_orgas_for_team(team: OrgaTeam) -> set[User]:
    """Return eligible organizers that are not assigned to this team."""
    party = party_service.get_party(team.party_id)

    assigned_orga_ids = set(
        db.session.scalars(
            select(DbMembership.user_id)
            .filter_by(orga_team_id=team.id)
        ).all()
    )

    unassigned_orga_ids_select = select(DbUser.id)

    if assigned_orga_ids:
        unassigned_orga_ids_select = unassigned_orga_ids_select \
            .filter(db.not_(DbUser.id.in_(assigned_orga_ids)))

    unassigned_orga_ids = set(
        db.session.scalars(
            unassigned_orga_ids_select
            .filter(DbUser.deleted == False)
            .join(DbOrgaFlag).filter(DbOrgaFlag.brand_id == party.brand_id)
        ).all()
    )

    return user_service.get_users(unassigned_orga_ids)


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


def select_orgas_for_party(
    user_ids: set[UserID], party_id: PartyID
) -> set[UserID]:
    """Return `True` if the user is an organizer (i.e. is member of an
    organizer team) of that party.
    """
    if not user_ids:
        return set()

    rows = db.session.scalars(
        select(DbMembership.user_id)
        .select_from(DbMembership)
        .filter(DbMembership.user_id.in_(user_ids))
        .join(DbOrgaTeam)
        .filter(DbOrgaTeam.party_id == party_id)
    ).all()

    return set(rows)
