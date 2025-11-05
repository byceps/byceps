"""
byceps.services.shop.order.actions.ticket_bundle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any
from uuid import UUID

from byceps.services.shop.order import (
    order_command_service,
    order_event_service,
    order_log_service,
)
from byceps.services.shop.order.models.order import LineItem, Order, OrderID
from byceps.services.ticketing import ticket_bundle_service
from byceps.services.ticketing.models.ticket import (
    TicketBundle,
    TicketBundleID,
    TicketCategory,
)
from byceps.services.user.models.user import User


def create_ticket_bundles(
    order: Order,
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
        order.id,
        initiator,
        ticket_category,
        owner,
        total_quantity,
    ).unwrap()
    order_event_service.send_tickets_sold_event(tickets_sold_event)


def _create_creation_order_log_entry(
    order_id: OrderID, ticket_bundle: TicketBundle
) -> None:
    event_type = 'ticket-bundle-created'

    data = {
        'ticket_bundle_id': str(ticket_bundle.id),
        'ticket_bundle_category_id': str(ticket_bundle.ticket_category.id),
        'ticket_bundle_ticket_quantity': ticket_bundle.ticket_quantity,
        'ticket_bundle_owner_id': str(ticket_bundle.owned_by.id),
    }

    order_log_service.create_db_entry(event_type, order_id, data)


def revoke_ticket_bundles(
    order: Order, line_item: LineItem, initiator: User
) -> None:
    """Revoke all ticket bundles related to the line item."""
    bundle_id_strs = line_item.processing_result['ticket_bundle_ids']
    bundle_ids = {
        TicketBundleID(UUID(bundle_id_str)) for bundle_id_str in bundle_id_strs
    }

    for bundle_id in bundle_ids:
        ticket_bundle_service.revoke_bundle(bundle_id, initiator)
        _create_revocation_order_log_entry(order.id, bundle_id, initiator)


def _create_revocation_order_log_entry(
    order_id: OrderID, bundle_id: TicketBundleID, initiator: User
) -> None:
    event_type = 'ticket-bundle-revoked'

    data = {
        'ticket_bundle_id': str(bundle_id),
        'initiator_id': str(initiator.id),
    }

    order_log_service.create_db_entry(event_type, order_id, data)
