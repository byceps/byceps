"""
byceps.services.ticketing.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType
from uuid import UUID

from attr import attrib, attrs

from ....typing import PartyID


TicketCategoryID = NewType('TicketCategoryID', UUID)


@attrs(frozen=True, slots=True)
class TicketCategory:
    id = attrib(type=TicketCategoryID)
    party_id = attrib(type=PartyID)
    title = attrib(type=str)


TicketCode = NewType('TicketCode', str)


TicketID = NewType('TicketID', UUID)


TicketBundleID = NewType('TicketBundleID', UUID)
