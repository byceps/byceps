"""
byceps.services.ticketing.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType
from uuid import UUID

from attr import attrs

from ....typing import PartyID


TicketCategoryID = NewType('TicketCategoryID', UUID)


@attrs(auto_attribs=True, frozen=True, slots=True)
class TicketCategory:
    id: TicketCategoryID
    party_id: PartyID
    title: str


TicketCode = NewType('TicketCode', str)


TicketID = NewType('TicketID', UUID)


TicketBundleID = NewType('TicketBundleID', UUID)
