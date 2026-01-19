"""
byceps.services.shop.order.actions.ticket
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Iterable
from typing import Any
from uuid import UUID

from byceps.services.shop.order import (
    order_command_service,
    order_event_service,
)
from byceps.services.shop.order.errors import OrderActionFailedError
from byceps.services.shop.order.log import (
    order_log_domain_service,
    order_log_service,
)
from byceps.services.shop.order.models.action import (
    ActionParameters,
    ActionProcedure,
)
from byceps.services.shop.order.models.order import (
    LineItem,
    Order,
    OrderID,
    PaidOrder,
)
from byceps.services.ticketing import (
    ticket_category_service,
    ticket_creation_service,
    ticket_revocation_service,
    ticket_service,
)
from byceps.services.ticketing.dbmodels.ticket import DbTicket
from byceps.services.ticketing.models.ticket import (
    TicketCategory,
    TicketCode,
    TicketID,
)
from byceps.services.user.models.user import User
from byceps.util.result import Ok, Result


def get_action_procedure() -> ActionProcedure:
    return ActionProcedure(
        on_payment=on_payment,
        on_cancellation_after_payment=on_cancellation_after_payment,
    )


def on_payment(
    order: PaidOrder,
    line_item: LineItem,
    initiator: User,
    parameters: ActionParameters,
) -> Result[None, OrderActionFailedError]:
    """Create tickets."""
    ticket_category_id = parameters['category_id']
    ticket_category = ticket_category_service.get_category(ticket_category_id)

    _create_tickets(order, line_item, ticket_category, initiator)

    return Ok(None)


def on_cancellation_after_payment(
    order: Order,
    line_item: LineItem,
    initiator: User,
    parameters: ActionParameters,
) -> Result[None, OrderActionFailedError]:
    """Revoke all tickets in the order."""
    _revoke_tickets(order, line_item, initiator)

    return Ok(None)


def _create_tickets(
    order: PaidOrder,
    line_item: LineItem,
    ticket_category: TicketCategory,
    initiator: User,
) -> None:
    """Create tickets."""
    owner = order.placed_by
    order_number = order.order_number
    ticket_quantity = line_item.quantity

    tickets = ticket_creation_service.create_tickets(
        ticket_category,
        owner,
        ticket_quantity,
        order_number=order_number,
        user=owner,
    )

    _create_creation_order_log_entries(order.id, tickets)

    data: dict[str, Any] = {
        'ticket_ids': list(sorted(str(ticket.id) for ticket in tickets))
    }
    order_command_service.update_line_item_processing_result(line_item.id, data)

    tickets_sold_event = order_event_service.create_tickets_sold_event(
        order, initiator, ticket_category, owner, ticket_quantity
    )
    order_event_service.send_tickets_sold_event(tickets_sold_event)


def _create_creation_order_log_entries(
    order_id: OrderID, tickets: Iterable[DbTicket]
) -> None:
    log_entries = [
        order_log_domain_service.build_ticket_created_entry(
            order_id,
            ticket.id,
            TicketCode(ticket.code),
            ticket.category_id,
            ticket.owned_by_id,
        )
        for ticket in tickets
    ]

    order_log_service.persist_entries(log_entries)


def _revoke_tickets(order: Order, line_item: LineItem, initiator: User) -> None:
    """Revoke all tickets related to the line item."""
    ticket_id_strs = line_item.processing_result['ticket_ids']
    ticket_ids = {
        TicketID(UUID(ticket_id_str)) for ticket_id_str in ticket_id_strs
    }
    tickets = ticket_service.get_tickets(ticket_ids)

    ticket_revocation_service.revoke_tickets(ticket_ids, initiator)

    _create_revocation_order_log_entries(order.id, tickets, initiator)


def _create_revocation_order_log_entries(
    order_id: OrderID, tickets: Iterable[DbTicket], initiator: User
) -> None:
    log_entries = [
        order_log_domain_service.build_ticket_revoked_entry(
            order_id, ticket.id, TicketCode(ticket.code), initiator
        )
        for ticket in tickets
    ]

    order_log_service.persist_entries(log_entries)
