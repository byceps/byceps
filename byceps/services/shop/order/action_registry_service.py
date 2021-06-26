"""
byceps.services.shop.order.action_registry_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...ticketing.transfer.models import TicketCategoryID
from ...user_badge.transfer.models import BadgeID

from ..article.transfer.models import ArticleNumber

from .transfer.models import ActionParameters, PaymentState

from . import action_service


def register_badge_awarding(
    article_number: ArticleNumber, badge_id: BadgeID
) -> None:
    # Award badge to orderer when order is marked as paid.
    params_create = {
        'badge_id': str(badge_id),
    }
    action_service.create_action(
        article_number, PaymentState.paid, 'create_tickets', params_create
    )


def register_ticket_bundles_creation(
    article_number: ArticleNumber,
    ticket_category_id: TicketCategoryID,
    ticket_quantity: int,
) -> None:
    # Create ticket bundle(s) for order when it is marked as paid.
    params_create = {
        'category_id': str(ticket_category_id),
        'ticket_quantity': ticket_quantity,
    }
    action_service.create_action(
        article_number,
        PaymentState.paid,
        'create_ticket_bundles',
        params_create,
    )

    # Revoke ticket bundles that have been created for the order when it
    # is canceled after being marked as paid.
    params_revoke: ActionParameters = {}
    action_service.create_action(
        article_number,
        PaymentState.canceled_after_paid,
        'revoke_ticket_bundles',
        params_revoke,
    )


def register_tickets_creation(
    article_number: ArticleNumber, ticket_category_id: TicketCategoryID
) -> None:
    # Create tickets for order when it is marked as paid.
    params_create = {
        'category_id': str(ticket_category_id),
    }
    action_service.create_action(
        article_number, PaymentState.paid, 'create_tickets', params_create
    )

    # Revoke tickets that have been created for the order when it is
    # canceled after being marked as paid.
    params_revoke: ActionParameters = {}
    action_service.create_action(
        article_number,
        PaymentState.canceled_after_paid,
        'revoke_tickets',
        params_revoke,
    )
