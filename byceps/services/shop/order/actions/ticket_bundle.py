"""
byceps.services.shop.order.actions.ticket_bundle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from .....typing import UserID

from ....ticketing.dbmodels.ticket_bundle import TicketBundle
from ....ticketing import (
    category_service as ticket_category_service,
    ticket_service,
    ticket_bundle_service,
)
from ....ticketing.transfer.models import TicketBundleID, TicketCategoryID

from .. import log_service
from ..transfer.order import Order, OrderID

from ._ticketing import create_tickets_sold_event, send_tickets_sold_event


def create_ticket_bundles(
    order: Order,
    ticket_category_id: TicketCategoryID,
    ticket_quantity_per_bundle: int,
    bundle_quantity: int,
    initiator_id: UserID,
) -> None:
    """Create ticket bundles."""
    owned_by_id = order.placed_by_id
    order_number = order.order_number

    ticket_category = ticket_category_service.get_category(ticket_category_id)

    for _ in range(bundle_quantity):
        bundle = ticket_bundle_service.create_bundle(
            ticket_category.party_id,
            ticket_category.id,
            ticket_quantity_per_bundle,
            owned_by_id,
            order_number=order_number,
            used_by_id=owned_by_id,
        )

        _create_creation_order_log_entry(order.id, bundle)

    tickets_sold_event = create_tickets_sold_event(
        order.id,
        initiator_id,
        ticket_category_id,
        owned_by_id,
        ticket_quantity_per_bundle,
    )
    send_tickets_sold_event(tickets_sold_event)


def _create_creation_order_log_entry(
    order_id: OrderID, ticket_bundle: TicketBundle
) -> None:
    event_type = 'ticket-bundle-created'

    data = {
        'ticket_bundle_id': str(ticket_bundle.id),
        'ticket_bundle_category_id': str(ticket_bundle.ticket_category_id),
        'ticket_bundle_ticket_quantity': ticket_bundle.ticket_quantity,
        'ticket_bundle_owner_id': str(ticket_bundle.owned_by_id),
    }

    log_service.create_entry(event_type, order_id, data)


def revoke_ticket_bundles(order: Order, initiator_id: UserID) -> None:
    """Revoke all ticket bundles in this order."""
    # Fetch all tickets, bundled or not.
    tickets = ticket_service.find_tickets_created_by_order(order.order_number)

    bundle_ids = {t.bundle_id for t in tickets if t.bundle_id}

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
