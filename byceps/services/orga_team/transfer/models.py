"""
byceps.services.orga_team.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from ....typing import PartyID, UserID


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
    duties: str
