"""
byceps.services.shop.order.action_registry_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ...ticketing.models.category import CategoryID
from ...user_badge.models.badge import BadgeID

from ..article.models.article import ArticleNumber

from .models.order_action import Parameters
from .models.payment import PaymentState

from . import action_service


def register_badge_awarding(article_number: ArticleNumber, badge_id: BadgeID
                           ) -> None:
    # Award badge to orderer when order is marked as paid.
    params_create = {
        'badge_id': str(badge_id),
    }
    action_service.create_action(article_number, PaymentState.paid,
                                 'create_tickets', params_create)


def register_ticket_bundles_creation(article_number: ArticleNumber,
                                     ticket_category_id: CategoryID,
                                     ticket_quantity: int) -> None:
    # Create ticket bundle(s) for order when it is marked as paid.
    params_create = {
        'category_id': str(ticket_category_id),
        'ticket_quantity': ticket_quantity,
    }
    action_service.create_action(article_number, PaymentState.paid,
                                 'create_ticket_bundles', params_create)


def register_tickets_creation(article_number: ArticleNumber,
                              ticket_category_id: CategoryID) -> None:
    # Create tickets for order when it is marked as paid.
    params_create = {
        'category_id': str(ticket_category_id),
    }
    action_service.create_action(article_number, PaymentState.paid,
                                 'create_tickets', params_create)

    # Revoke tickets that have been created for order when it is
    # canceled after being marked as paid.
    params_revoke = {}  # type: Parameters
    action_service.create_action(article_number, PaymentState.canceled_after_paid,
                                 'revoke_tickets', params_revoke)
