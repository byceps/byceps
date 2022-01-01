"""
byceps.services.shop.order.actions.revoke_ticket_bundles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from .....typing import UserID

from ....ticketing import ticket_bundle_service, ticket_service
from ....ticketing.transfer.models import TicketBundleID

from ...article.transfer.models import ArticleNumber

from .. import log_service
from ..transfer.action import ActionParameters
from ..transfer.order import Order, OrderID


def revoke_ticket_bundles(
    order: Order,
    article_number: ArticleNumber,
    bundle_quantity: int,
    initiator_id: UserID,
    parameters: ActionParameters,
) -> None:
    """Revoke all ticket bundles in this order."""
    # Fetch all tickets, bundled or not.
    tickets = ticket_service.find_tickets_created_by_order(order.order_number)

    bundle_ids = {t.bundle_id for t in tickets if t.bundle_id}

    for bundle_id in bundle_ids:
        ticket_bundle_service.revoke_bundle(bundle_id, initiator_id)
        _create_order_log_entry(order.id, bundle_id, initiator_id)


def _create_order_log_entry(
    order_id: OrderID, bundle_id: TicketBundleID, initiator_id: UserID
) -> None:
    event_type = 'ticket-bundle-revoked'

    data = {
        'ticket_bundle_id': str(bundle_id),
        'initiator_id': str(initiator_id),
    }

    log_service.create_entry(event_type, order_id, data)
