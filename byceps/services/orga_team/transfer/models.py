"""
byceps.services.orga_team.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType
from uuid import UUID


OrgaTeamID = NewType('OrgaTeamID', UUID)


MembershipID = NewType('MembershipID', UUID)
