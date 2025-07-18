"""
byceps.services.ticketing.models.ticket
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

from byceps.services.party.models import PartyID
from byceps.services.user.models.user import User


TicketCategoryID = NewType('TicketCategoryID', UUID)


@dataclass(frozen=True, kw_only=True)
class TicketCategory:
    id: TicketCategoryID
    party_id: PartyID
    title: str


TicketCode = NewType('TicketCode', str)


TicketID = NewType('TicketID', UUID)


TicketBundleID = NewType('TicketBundleID', UUID)


@dataclass(frozen=True, kw_only=True)
class TicketBundle:
    id: TicketBundleID
    created_at: datetime
    party_id: PartyID
    ticket_category: TicketCategory
    ticket_quantity: int
    owned_by: User
    seats_managed_by: User | None
    users_managed_by: User | None
    label: str | None
    revoked: bool
    ticket_ids: set[TicketID]


@dataclass(frozen=True, kw_only=True)
class TicketSaleStats:
    tickets_max: int | None
    tickets_sold: int
