"""
byceps.services.shop.order.order_action_registry_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.shop.product.models import ProductID
from byceps.services.ticketing.models.ticket import TicketCategoryID
from byceps.services.user_badge.models import BadgeID

from . import order_action_service


def register_badge_awarding(product_id: ProductID, badge_id: BadgeID) -> None:
    # Award badge to orderer when order is marked as paid.
    params_create = {
        'badge_id': str(badge_id),
    }
    order_action_service.create_action(product_id, 'award_badge', params_create)


def register_ticket_bundles_creation(
    product_id: ProductID,
    ticket_category_id: TicketCategoryID,
    ticket_quantity: int,
) -> None:
    # Create ticket bundle(s) for order when it is marked as paid.
    params_create = {
        'category_id': str(ticket_category_id),
        'ticket_quantity': ticket_quantity,
    }
    order_action_service.create_action(
        product_id, 'create_ticket_bundles', params_create
    )


def register_tickets_creation(
    product_id: ProductID,
    ticket_category_id: TicketCategoryID,
) -> None:
    # Create tickets for order when it is marked as paid.
    params_create = {
        'category_id': str(ticket_category_id),
    }
    order_action_service.create_action(
        product_id, 'create_tickets', params_create
    )
