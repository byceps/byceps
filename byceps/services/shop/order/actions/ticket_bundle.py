"""
byceps.services.shop.order.actions.ticket_bundle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Any
from uuid import UUID

from .....typing import UserID

from ....ticketing.dbmodels.ticket_bundle import DbTicketBundle
from ....ticketing import (
    category_service as ticket_category_service,
    ticket_bundle_service,
)
from ....ticketing.transfer.models import TicketBundleID, TicketCategoryID

from .. import log_service, service as order_service
from ..transfer.order import LineItem, Order, OrderID

from ._ticketing import create_tickets_sold_event, send_tickets_sold_event


def create_ticket_bundles(
    order: Order,
    line_item: LineItem,
    ticket_category_id: TicketCategoryID,
    ticket_quantity_per_bundle: int,
    initiator_id: UserID,
) -> None:
    """Create ticket bundles."""
    owned_by_id = order.placed_by_id
    order_number = order.order_number
    bundle_quantity = line_item.quantity

    ticket_category = ticket_category_service.get_category(ticket_category_id)

    bundle_ids = set()
    for _ in range(bundle_quantity):
        bundle = ticket_bundle_service.create_bundle(
            ticket_category.party_id,
            ticket_category.id,
            ticket_quantity_per_bundle,
            owned_by_id,
            order_number=order_number,
            used_by_id=owned_by_id,
        )

        bundle_ids.add(bundle.id)

        _create_creation_order_log_entry(order.id, bundle)

    data: dict[str, Any] = {
        'ticket_bundle_ids': list(
            sorted(str(bundle_id) for bundle_id in bundle_ids)
        )
    }
    order_service.update_line_item_processing_result(line_item.id, data)

    total_quantity = ticket_quantity_per_bundle * bundle_quantity
    tickets_sold_event = create_tickets_sold_event(
        order.id,
        initiator_id,
        ticket_category_id,
        owned_by_id,
        total_quantity,
    )
    send_tickets_sold_event(tickets_sold_event)


def _create_creation_order_log_entry(
    order_id: OrderID, ticket_bundle: DbTicketBundle
) -> None:
    event_type = 'ticket-bundle-created'

    data = {
        'ticket_bundle_id': str(ticket_bundle.id),
        'ticket_bundle_category_id': str(ticket_bundle.ticket_category_id),
        'ticket_bundle_ticket_quantity': ticket_bundle.ticket_quantity,
        'ticket_bundle_owner_id': str(ticket_bundle.owned_by_id),
    }

    log_service.create_entry(event_type, order_id, data)


def revoke_ticket_bundles(
    order: Order, line_item: LineItem, initiator_id: UserID
) -> None:
    """Revoke all ticket bundles related to the line item."""
    bundle_id_strs = line_item.processing_result['ticket_bundle_ids']
    bundle_ids = {
        TicketBundleID(UUID(bundle_id_str)) for bundle_id_str in bundle_id_strs
    }

    for bundle_id in bundle_ids:
        ticket_bundle_service.revoke_bundle(bundle_id, initiator_id)
        _create_revocation_order_log_entry(order.id, bundle_id, initiator_id)


def _create_revocation_order_log_entry(
    order_id: OrderID, bundle_id: TicketBundleID, initiator_id: UserID
) -> None:
    event_type = 'ticket-bundle-revoked'

    data = {
        'ticket_bundle_id': str(bundle_id),
        'initiator_id': str(initiator_id),
    }

    log_service.create_entry(event_type, order_id, data)
