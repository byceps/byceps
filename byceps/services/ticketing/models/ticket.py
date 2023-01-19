"""
byceps.services.ticketing.models.ticket
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType, Optional
from uuid import UUID

from ....typing import PartyID


TicketCategoryID = NewType('TicketCategoryID', UUID)


@dataclass(frozen=True)
class TicketCategory:
    id: TicketCategoryID
    party_id: PartyID
    title: str


TicketCode = NewType('TicketCode', str)


TicketID = NewType('TicketID', UUID)


TicketBundleID = NewType('TicketBundleID', UUID)


@dataclass(frozen=True)
class TicketSaleStats:
    tickets_max: Optional[int]
    tickets_sold: int
