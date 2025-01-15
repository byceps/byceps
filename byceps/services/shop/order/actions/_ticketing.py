"""
byceps.services.shop.order.actions._ticketing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.events.base import EventParty, EventUser
from byceps.events.ticketing import TicketsSoldEvent
from byceps.services.party import party_service
from byceps.services.shop.order import order_service
from byceps.services.shop.order.errors import OrderNotPaidError
from byceps.services.shop.order.models.order import OrderID
from byceps.services.ticketing import ticket_category_service
from byceps.services.ticketing.models.ticket import TicketCategoryID
from byceps.services.user.models.user import User
from byceps.signals import ticketing as ticketing_signals
from byceps.util.result import Err, Ok, Result


def create_tickets_sold_event(
    order_id: OrderID,
    initiator: User,
    category_id: TicketCategoryID,
    owner: User,
    quantity: int,
) -> Result[TicketsSoldEvent, OrderNotPaidError]:
    order_paid_at_result = order_service.get_payment_date(order_id)
    if order_paid_at_result.is_err():
        return Err(order_paid_at_result.unwrap_err())

    paid_at = order_paid_at_result.unwrap()
    category = ticket_category_service.get_category(category_id)
    party = party_service.get_party(category.party_id)

    event = TicketsSoldEvent(
        occurred_at=paid_at,
        initiator=EventUser.from_user(initiator),
        party=EventParty.from_party(party),
        owner=EventUser.from_user(owner),
        quantity=quantity,
    )

    return Ok(event)


def send_tickets_sold_event(event: TicketsSoldEvent) -> None:
    ticketing_signals.tickets_sold.send(None, event=event)
