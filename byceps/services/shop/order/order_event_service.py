"""
byceps.services.shop.order.order_event_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.core.events import EventParty
from byceps.services.party import party_service
from byceps.services.shop.order.models.order import PaidOrder
from byceps.services.ticketing import signals as ticketing_signals
from byceps.services.ticketing.events import TicketsSoldEvent
from byceps.services.ticketing.models.ticket import TicketCategory
from byceps.services.user.models.user import User


def create_tickets_sold_event(
    order: PaidOrder,
    initiator: User,
    category: TicketCategory,
    owner: User,
    quantity: int,
) -> TicketsSoldEvent:
    party = party_service.get_party(category.party_id)

    return TicketsSoldEvent(
        occurred_at=order.paid_at,
        initiator=initiator,
        party=EventParty.from_party(party),
        owner=owner,
        quantity=quantity,
    )


def send_tickets_sold_event(event: TicketsSoldEvent) -> None:
    ticketing_signals.tickets_sold.send(None, event=event)
