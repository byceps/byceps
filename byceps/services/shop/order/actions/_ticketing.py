"""
byceps.services.shop.order.actions._ticketing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from .....events.ticketing import TicketsSold
from .....signals import ticketing as ticketing_signals
from .....typing import UserID

from ....ticketing import category_service
from ....ticketing.transfer.models import TicketCategoryID
from ....user import service as user_service


def create_tickets_sold_event(
    initiator_id: UserID,
    category_id: TicketCategoryID,
    owner_id: UserID,
    quantity: int,
) -> TicketsSold:
    occurred_at = datetime.utcnow()
    initiator_screen_name = user_service.find_screen_name(initiator_id)
    category = category_service.find_category(category_id)
    owner_screen_name = user_service.find_screen_name(owner_id)

    return TicketsSold(
        occurred_at=occurred_at,
        initiator_id=initiator_id,
        initiator_screen_name=initiator_screen_name,
        party_id=category.party_id,
        owner_id=owner_id,
        owner_screen_name=owner_screen_name,
        quantity=quantity,
    )


def send_tickets_sold_event(event: TicketsSold) -> None:
    ticketing_signals.tickets_sold.send(None, event=event)
