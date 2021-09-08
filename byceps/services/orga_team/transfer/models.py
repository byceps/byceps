"""
byceps.services.orga_team.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType, Optional
from uuid import UUID

from ....typing import PartyID, UserID

from ...party.transfer.models import Party
from ...user.transfer.models import User


OrgaTeamID = NewType('OrgaTeamID', UUID)


@dataclass(frozen=True)
class OrgaTeam:
    id: OrgaTeamID
    party_id: PartyID
    title: str


MembershipID = NewType('MembershipID', UUID)


@dataclass(frozen=True)
class Membership:
    id: MembershipID
    orga_team_id: OrgaTeamID
    user_id: UserID
    duties: Optional[str]


@dataclass(frozen=True)
class Member:
    membership: Membership
    user: User


@dataclass(frozen=True)
class OrgaActivity:
    user_id: UserID
    party: Party
    team: OrgaTeam
    duties: Optional[str]


@dataclass(frozen=True)
class PublicOrga:
    user: User
    full_name: str
    team_name: str
    duties: Optional[str]
