"""
byceps.services.orga_team.orga_team_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from itertools import groupby
from typing import Iterable, Optional

from sqlalchemy import delete, select

from ...database import db
from ...typing import PartyID, UserID

from ..orga.dbmodels import DbOrgaFlag
from ..party import party_service
from ..user.dbmodels.detail import DbUserDetail
from ..user.dbmodels.user import DbUser
from ..user.models.user import User
from ..user import user_service

from .dbmodels import DbMembership, DbOrgaTeam
from .models import (
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
    db_team = DbOrgaTeam(party_id, title)

    db.session.add(db_team)
    db.session.commit()

    return _db_entity_to_team(db_team)


def delete_team(team_id: OrgaTeamID) -> None:
    """Delete the orga team."""
    db.session.execute(delete(DbOrgaTeam).filter_by(id=team_id))
    db.session.commit()


def count_teams_for_parties(party_ids: set[PartyID]) -> dict[PartyID, int]:
    """Count orga teams for each party."""
    party_ids_and_team_counts = db.session.execute(
        select(DbOrgaTeam.party_id, db.func.count(DbOrgaTeam.id))
        .filter(DbOrgaTeam.party_id.in_(party_ids))
        .group_by(DbOrgaTeam.party_id)
    ).all()

    return dict(party_ids_and_team_counts)


def count_teams_for_party(party_id: PartyID) -> int:
    """Return the number of orga teams for that party."""
    return db.session.scalar(
        select(db.func.count(DbOrgaTeam.id)).filter_by(party_id=party_id)
    )


def get_teams_for_party(party_id: PartyID) -> set[OrgaTeam]:
    """Return orga teams for that party."""
    db_teams = db.session.scalars(
        select(DbOrgaTeam).filter_by(party_id=party_id)
    ).all()

    return {_db_entity_to_team(db_team) for db_team in db_teams}


def find_team(team_id: OrgaTeamID) -> Optional[OrgaTeam]:
    """Return the team with that id, or `None` if not found."""
    db_team = _find_db_team(team_id)

    if db_team is None:
        return None

    return _db_entity_to_team(db_team)


def _find_db_team(team_id: OrgaTeamID) -> Optional[DbOrgaTeam]:
    """Return the team with that id, or `None` if not found."""
    return db.session.get(DbOrgaTeam, team_id)


def get_teams_and_members_for_party(
    party_id: PartyID,
) -> list[tuple[OrgaTeam, set[Member]]]:
    """Return all orga teams and their corresponding memberships for
    that party.
    """
    db_teams = (
        db.session.scalars(
            select(DbOrgaTeam)
            .options(db.joinedload(DbOrgaTeam.memberships))
            .filter_by(party_id=party_id)
        )
        .unique()
        .all()
    )

    user_ids = {
        db_ms.user_id for db_team in db_teams for db_ms in db_team.memberships
    }
    users = user_service.get_users(user_ids, include_avatars=True)
    users_by_id = user_service.index_users_by_id(users)

    def to_member(db_membership: DbMembership) -> Member:
        membership = _db_entity_to_membership(db_membership)
        user = users_by_id[membership.user_id]

        return Member(membership, user)

    return [
        (
            _db_entity_to_team(db_team),
            {to_member(db_ms) for db_ms in db_team.memberships},
        )
        for db_team in db_teams
    ]


def _db_entity_to_team(db_team: DbOrgaTeam) -> OrgaTeam:
    return OrgaTeam(
        id=db_team.id,
        party_id=db_team.party_id,
        title=db_team.title,
    )


# -------------------------------------------------------------------- #
# memberships


def create_membership(
    team_id: OrgaTeamID, user_id: UserID, duties: Optional[str]
) -> Membership:
    """Assign the user to the team."""
    db_membership = DbMembership(team_id, user_id, duties=duties)

    db.session.add(db_membership)
    db.session.commit()

    return _db_entity_to_membership(db_membership)


def update_membership(
    membership_id: MembershipID, team_id: OrgaTeamID, duties: str
) -> Membership:
    """Update the membership."""
    db_membership = _find_db_membership(membership_id)
    if db_membership is None:
        raise ValueError(f"Unknown membership ID '{membership_id}'")

    db_team = _find_db_team(team_id)
    if db_team is None:
        raise ValueError(f"Unknown team ID '{team_id}'")

    db_membership.orga_team = db_team
    db_membership.duties = duties
    db.session.commit()

    return _db_entity_to_membership(db_membership)


def delete_membership(membership_id: MembershipID) -> None:
    """Delete the membership."""
    db.session.execute(delete(DbMembership).filter_by(id=membership_id))
    db.session.commit()


def count_memberships_for_party(party_id: PartyID) -> int:
    """Return the number of memberships the party's teams have in total."""
    return db.session.scalar(
        select(db.func.count(DbMembership.id))
        .join(DbOrgaTeam)
        .filter(DbOrgaTeam.party_id == party_id)
    )


def get_memberships_for_party(party_id: PartyID) -> set[Membership]:
    """Return memberships for that party."""
    db_memberships = db.session.scalars(
        select(DbMembership)
        .join(DbOrgaTeam)
        .filter(DbOrgaTeam.party_id == party_id)
    ).all()

    return {
        _db_entity_to_membership(db_membership)
        for db_membership in db_memberships
    }


def find_membership(membership_id: MembershipID) -> Optional[Membership]:
    """Return the membership with that id, or `None` if not found."""
    db_membership = _find_db_membership(membership_id)

    if db_membership is None:
        return None

    return _db_entity_to_membership(db_membership)


def _find_db_membership(membership_id: MembershipID) -> Optional[DbMembership]:
    """Return the membership with that id, or `None` if not found."""
    return db.session.get(DbMembership, membership_id)


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
    db_memberships = db.session.scalars(
        select(DbMembership)
        .options(db.joinedload(DbMembership.orga_team))
        .filter_by(user_id=user_id)
    ).all()

    party_ids = {ms.orga_team.party_id for ms in db_memberships}
    parties = party_service.get_parties(party_ids)
    parties_by_id = {party.id: party for party in parties}

    def to_activity(
        user_id: UserID,
        party_id: PartyID,
        db_memberships: Iterable[DbMembership],
    ) -> OrgaActivity:
        return OrgaActivity(
            user_id=user_id,
            party=parties_by_id[party_id],
            teams_and_duties=to_teams_and_duties(db_memberships),
        )

    def to_teams_and_duties(
        db_memberships: Iterable[DbMembership],
    ) -> frozenset[TeamAndDuties]:
        return frozenset(
            TeamAndDuties(
                team_title=db_ms.orga_team.title,
                duties=db_ms.duties,
            )
            for db_ms in db_memberships
        )

    def get_user_and_party(db_ms: DbMembership) -> tuple[UserID, PartyID]:
        return db_ms.user_id, db_ms.orga_team.party_id

    return {
        to_activity(user_id, party_id, db_ms)
        for (user_id, party_id), db_ms in groupby(
            sorted(db_memberships, key=get_user_and_party),
            key=get_user_and_party,
        )
    }


def get_public_orgas_for_party(party_id: PartyID) -> set[PublicOrga]:
    """Return all public orgas for that party."""
    db_memberships = db.session.scalars(
        select(DbMembership)
        .join(DbOrgaTeam)
        .filter(DbOrgaTeam.party_id == party_id)
        .options(
            db.joinedload(DbMembership.orga_team),
            db.joinedload(DbMembership.user).load_only(DbUser.id),
            db.joinedload(DbMembership.user)
            .joinedload(DbUser.detail)
            .load_only(DbUserDetail.first_name, DbUserDetail.last_name),
        )
    ).all()

    users_by_id = _get_public_orga_users_by_id(db_memberships)

    def to_orga(db_membership: DbMembership) -> PublicOrga:
        user = users_by_id[db_membership.user_id]

        return PublicOrga(
            user=user,
            full_name=db_membership.user.detail.full_name,
            team_name=db_membership.orga_team.title,
            duties=db_membership.duties,
        )

    orgas = {to_orga(db_ms) for db_ms in db_memberships}
    orgas = {orga for orga in orgas if not orga.user.deleted}

    return orgas


def _get_public_orga_users_by_id(
    db_memberships: DbMembership,
) -> dict[UserID, User]:
    user_ids = {db_ms.user_id for db_ms in db_memberships}
    users = user_service.get_users(user_ids, include_avatars=True)
    return user_service.index_users_by_id(users)


def has_team_memberships(team_id: OrgaTeamID) -> bool:
    """Return `True` if the team has memberships."""
    return db.session.scalar(
        select(db.exists().where(DbMembership.orga_team_id == team_id))
    )


def _db_entity_to_membership(db_membership: DbMembership) -> Membership:
    return Membership(
        id=db_membership.id,
        orga_team_id=db_membership.orga_team_id,
        user_id=db_membership.user_id,
        duties=db_membership.duties,
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
            select(DbMembership.user_id).filter_by(orga_team_id=team.id)
        ).all()
    )

    unassigned_orga_ids_select = select(DbUser.id)

    if assigned_orga_ids:
        unassigned_orga_ids_select = unassigned_orga_ids_select.filter(
            db.not_(DbUser.id.in_(assigned_orga_ids))
        )

    unassigned_orga_ids = set(
        db.session.scalars(
            unassigned_orga_ids_select.filter(
                DbUser.deleted == False  # noqa: E712
            )
            .join(DbOrgaFlag)
            .filter(DbOrgaFlag.brand_id == party.brand_id)
        ).all()
    )

    return user_service.get_users(unassigned_orga_ids)


def is_orga_for_party(user_id: UserID, party_id: PartyID) -> bool:
    """Return `True` if the user is an organizer (i.e. is member of an
    organizer team) of that party.
    """
    return db.session.scalar(
        select(
            select(DbMembership)
            .join(DbOrgaTeam)
            .filter(DbMembership.user_id == user_id)
            .filter(DbOrgaTeam.party_id == party_id)
            .exists()
        )
    )


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
