"""
byceps.services.shop.order.actions.ticket
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any, Iterable
from uuid import UUID

from .....typing import UserID

from ....ticketing import (
    ticket_category_service,
    ticket_creation_service,
    ticket_revocation_service,
    ticket_service,
)
from ....ticketing.dbmodels.ticket import DbTicket
from ....ticketing.models.ticket import TicketCategoryID, TicketID

from .. import order_log_service, order_service
from ..models.order import LineItem, Order, OrderID

from ._ticketing import create_tickets_sold_event, send_tickets_sold_event


def create_tickets(
    order: Order,
    line_item: LineItem,
    ticket_category_id: TicketCategoryID,
    initiator_id: UserID,
) -> None:
    """Create tickets."""
    owned_by_id = order.placed_by_id
    order_number = order.order_number
    ticket_quantity = line_item.quantity

    ticket_category = ticket_category_service.get_category(ticket_category_id)

    tickets = ticket_creation_service.create_tickets(
        ticket_category.party_id,
        ticket_category_id,
        owned_by_id,
        ticket_quantity,
        order_number=order_number,
        used_by_id=owned_by_id,
    )

    _create_creation_order_log_entries(order.id, tickets)

    data: dict[str, Any] = {
        'ticket_ids': list(sorted(str(ticket.id) for ticket in tickets))
    }
    order_service.update_line_item_processing_result(line_item.id, data)

    tickets_sold_event = create_tickets_sold_event(
        order.id, initiator_id, ticket_category_id, owned_by_id, ticket_quantity
    )
    send_tickets_sold_event(tickets_sold_event)


def _create_creation_order_log_entries(
    order_id: OrderID, tickets: Iterable[DbTicket]
) -> None:
    event_type = 'ticket-created'

    datas = [
        {
            'ticket_id': str(ticket.id),
            'ticket_code': ticket.code,
            'ticket_category_id': str(ticket.category_id),
            'ticket_owner_id': str(ticket.owned_by_id),
        }
        for ticket in tickets
    ]

    order_log_service.create_entries(event_type, order_id, datas)


def revoke_tickets(
    order: Order, line_item: LineItem, initiator_id: UserID
) -> None:
    """Revoke all tickets related to the line item."""
    ticket_id_strs = line_item.processing_result['ticket_ids']
    ticket_ids = {
        TicketID(UUID(ticket_id_str)) for ticket_id_str in ticket_id_strs
    }
    tickets = ticket_service.get_tickets(ticket_ids)

    ticket_revocation_service.revoke_tickets(ticket_ids, initiator_id)

    _create_revocation_order_log_entries(order.id, tickets, initiator_id)


def _create_revocation_order_log_entries(
    order_id: OrderID, tickets: Iterable[DbTicket], initiator_id: UserID
) -> None:
    event_type = 'ticket-revoked'

    datas = [
        {
            'ticket_id': str(ticket.id),
            'ticket_code': ticket.code,
            'initiator_id': str(initiator_id),
        }
        for ticket in tickets
    ]

    order_log_service.create_entries(event_type, order_id, datas)
