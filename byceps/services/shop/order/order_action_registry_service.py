"""
byceps.services.shop.order.order_action_registry_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...ticketing.transfer.models import TicketCategoryID
from ...user_badge.models import BadgeID

from ..article.transfer.models import ArticleID

from .transfer.action import ActionParameters
from .transfer.order import PaymentState

from . import order_action_service


def register_badge_awarding(article_id: ArticleID, badge_id: BadgeID) -> None:
    # Award badge to orderer when order is marked as paid.
    params_create = {
        'badge_id': str(badge_id),
    }
    order_action_service.create_action(
        article_id, PaymentState.paid, 'award_badge', params_create
    )


def register_ticket_bundles_creation(
    article_id: ArticleID,
    ticket_category_id: TicketCategoryID,
    ticket_quantity: int,
) -> None:
    # Create ticket bundle(s) for order when it is marked as paid.
    params_create = {
        'category_id': str(ticket_category_id),
        'ticket_quantity': ticket_quantity,
    }
    order_action_service.create_action(
        article_id, PaymentState.paid, 'create_ticket_bundles', params_create
    )

    # Revoke ticket bundles that have been created for the order when it
    # is canceled after being marked as paid.
    params_revoke: ActionParameters = {}
    order_action_service.create_action(
        article_id,
        PaymentState.canceled_after_paid,
        'revoke_ticket_bundles',
        params_revoke,
    )


def register_tickets_creation(
    article_id: ArticleID,
    ticket_category_id: TicketCategoryID,
) -> None:
    # Create tickets for order when it is marked as paid.
    params_create = {
        'category_id': str(ticket_category_id),
    }
    order_action_service.create_action(
        article_id, PaymentState.paid, 'create_tickets', params_create
    )

    # Revoke tickets that have been created for the order when it is
    # canceled after being marked as paid.
    params_revoke: ActionParameters = {}
    order_action_service.create_action(
        article_id,
        PaymentState.canceled_after_paid,
        'revoke_tickets',
        params_revoke,
    )
