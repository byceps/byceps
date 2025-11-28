"""
byceps.services.shop.order.actions.ticket_bundle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any
from uuid import UUID

from byceps.services.seating.errors import SeatingError
from byceps.services.shop.order import (
    order_command_service,
    order_event_service,
    order_log_domain_service,
    order_log_service,
)
from byceps.services.shop.order.errors import OrderActionFailedError
from byceps.services.shop.order.models.action import ActionParameters
from byceps.services.shop.order.models.order import (
    LineItem,
    Order,
    OrderID,
    PaidOrder,
)
from byceps.services.ticketing import (
    ticket_bundle_service,
    ticket_category_service,
)
from byceps.services.ticketing.models.ticket import (
    TicketBundle,
    TicketBundleID,
    TicketCategory,
)
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result


def on_payment(
    order: PaidOrder,
    line_item: LineItem,
    initiator: User,
    parameters: ActionParameters,
) -> Result[None, OrderActionFailedError]:
    """Create ticket bundles."""
    ticket_category_id = parameters['category_id']
    ticket_category = ticket_category_service.get_category(ticket_category_id)

    ticket_quantity_per_bundle = parameters['ticket_quantity']

    _create_ticket_bundles(
        order,
        line_item,
        ticket_category,
        ticket_quantity_per_bundle,
        initiator,
    )

    return Ok(None)


def on_cancellation_after_payment(
    order: Order,
    line_item: LineItem,
    initiator: User,
    parameters: ActionParameters,
) -> Result[None, OrderActionFailedError]:
    """Revoke all ticket bundles in this order."""
    match _revoke_ticket_bundles(order, line_item, initiator):
        case Ok(_):
            return Ok(None)
        case Err(e):
            return Err(OrderActionFailedError(e))


def _create_ticket_bundles(
    order: PaidOrder,
    line_item: LineItem,
    ticket_category: TicketCategory,
    ticket_quantity_per_bundle: int,
    initiator: User,
) -> None:
    """Create ticket bundles."""
    owner = order.placed_by
    order_number = order.order_number
    bundle_quantity = line_item.quantity

    bundle_ids = set()
    for _ in range(bundle_quantity):
        bundle = ticket_bundle_service.create_bundle(
            ticket_category,
            ticket_quantity_per_bundle,
            owner,
            order_number=order_number,
            user=owner,
        )

        bundle_ids.add(bundle.id)

        _create_creation_order_log_entry(order.id, bundle)

    data: dict[str, Any] = {
        'ticket_bundle_ids': list(
            sorted(str(bundle_id) for bundle_id in bundle_ids)
        )
    }
    order_command_service.update_line_item_processing_result(line_item.id, data)

    total_quantity = ticket_quantity_per_bundle * bundle_quantity
    tickets_sold_event = order_event_service.create_tickets_sold_event(
        order,
        initiator,
        ticket_category,
        owner,
        total_quantity,
    )
    order_event_service.send_tickets_sold_event(tickets_sold_event)


def _create_creation_order_log_entry(
    order_id: OrderID, ticket_bundle: TicketBundle
) -> None:
    log_entry = order_log_domain_service.build_ticket_bundle_created_entry(
        order_id,
        ticket_bundle.id,
        ticket_bundle.ticket_category.id,
        ticket_bundle.ticket_quantity,
        ticket_bundle.owned_by.id,
    )

    order_log_service.persist_entry(log_entry)


def _revoke_ticket_bundles(
    order: Order, line_item: LineItem, initiator: User
) -> Result[None, SeatingError]:
    """Revoke all ticket bundles related to the line item."""
    bundle_id_strs = line_item.processing_result['ticket_bundle_ids']
    bundle_ids = {
        TicketBundleID(UUID(bundle_id_str)) for bundle_id_str in bundle_id_strs
    }

    for bundle_id in bundle_ids:
        match ticket_bundle_service.revoke_bundle(bundle_id, initiator):
            case Err(e):
                return Err(e)

        _create_revocation_order_log_entry(order.id, bundle_id, initiator)

    return Ok(None)


def _create_revocation_order_log_entry(
    order_id: OrderID, ticket_bundle_id: TicketBundleID, initiator: User
) -> None:
    log_entry = order_log_domain_service.build_ticket_bundle_revoked_entry(
        order_id, ticket_bundle_id, initiator
    )

    order_log_service.persist_entry(log_entry)
