"""
byceps.services.orga_team.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from byceps.services.party.models import Party, PartyID
from byceps.services.user.models.user import User, UserID


OrgaTeamID = NewType('OrgaTeamID', UUID)


@dataclass(frozen=True, kw_only=True)
class OrgaTeam:
    id: OrgaTeamID
    party_id: PartyID
    title: str


MembershipID = NewType('MembershipID', UUID)


@dataclass(frozen=True, kw_only=True)
class Membership:
    id: MembershipID
    orga_team_id: OrgaTeamID
    user_id: UserID
    duties: str | None


@dataclass(frozen=True, kw_only=True)
class Member:
    membership: Membership
    user: User


@dataclass(frozen=True, kw_only=True)
class TeamAndDuties:
    team_title: str
    duties: str | None


@dataclass(frozen=True, kw_only=True)
class OrgaActivity:
    user_id: UserID
    party: Party
    teams_and_duties: frozenset[TeamAndDuties]


@dataclass(frozen=True, kw_only=True)
class PublicOrga:
    user: User
    full_name: str
    team_name: str
    duties: str | None
