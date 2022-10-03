"""
byceps.services.shop.order.actions._ticketing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from .....events.ticketing import TicketsSold
from .....signals import ticketing as ticketing_signals
from .....typing import UserID

from ....ticketing import category_service
from ....ticketing.transfer.models import TicketCategoryID
from ....user import service as user_service

from .. import order_service
from ..transfer.order import OrderID


def create_tickets_sold_event(
    order_id: OrderID,
    initiator_id: UserID,
    category_id: TicketCategoryID,
    owner_id: UserID,
    quantity: int,
) -> TicketsSold:
    occurred_at = order_service.get_payment_date(order_id)
    initiator_screen_name = user_service.find_screen_name(initiator_id)
    category = category_service.get_category(category_id)
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
