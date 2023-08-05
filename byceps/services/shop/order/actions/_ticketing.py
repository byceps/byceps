"""
byceps.services.shop.order.actions._ticketing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.events.ticketing import TicketsSoldEvent
from byceps.services.shop.order import order_service
from byceps.services.shop.order.models.order import OrderID
from byceps.services.ticketing import ticket_category_service
from byceps.services.ticketing.models.ticket import TicketCategoryID
from byceps.services.user.models.user import User
from byceps.signals import ticketing as ticketing_signals


def create_tickets_sold_event(
    order_id: OrderID,
    initiator: User,
    category_id: TicketCategoryID,
    owner: User,
    quantity: int,
) -> TicketsSoldEvent:
    occurred_at = order_service.get_payment_date(order_id)
    category = ticket_category_service.get_category(category_id)

    return TicketsSoldEvent(
        occurred_at=occurred_at,
        initiator_id=initiator.id,
        initiator_screen_name=initiator.screen_name,
        party_id=category.party_id,
        owner_id=owner.id,
        owner_screen_name=owner.screen_name,
        quantity=quantity,
    )


def send_tickets_sold_event(event: TicketsSoldEvent) -> None:
    ticketing_signals.tickets_sold.send(None, event=event)
