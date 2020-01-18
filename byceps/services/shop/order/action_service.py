"""
byceps.services.shop.order.action_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Callable, Sequence, Set

from ....database import db
from ....typing import UserID

from ..article.models.article import Article
from ..article.transfer.models import ArticleNumber
from ..shop.transfer.models import ShopID

from .actions.award_badge import award_badge
from .actions.create_ticket_bundles import create_ticket_bundles
from .actions.create_tickets import create_tickets
from .actions.revoke_ticket_bundles import revoke_ticket_bundles
from .actions.revoke_tickets import revoke_tickets
from .models.order_action import OrderAction, Parameters
from .transfer.models import Order, PaymentState


OrderActionType = Callable[[Order, ArticleNumber, int, Parameters], None]


PROCEDURES_BY_NAME = {
    'award_badge': award_badge,
    'create_ticket_bundles': create_ticket_bundles,
    'revoke_ticket_bundles': revoke_ticket_bundles,
    'create_tickets': create_tickets,
    'revoke_tickets': revoke_tickets,
}


# -------------------------------------------------------------------- #
# creation


def create_action(
    article_number: ArticleNumber,
    payment_state: PaymentState,
    procedure: str,
    parameters: Parameters,
) -> None:
    """Create an order action."""
    action = OrderAction(article_number, payment_state, procedure, parameters)

    db.session.add(action)
    db.session.commit()


# -------------------------------------------------------------------- #
# retrieval


def get_actions(shop_id: ShopID) -> Sequence[OrderAction]:
    """Return all order actions defined for articles of that shop."""
    return OrderAction.query \
        .join(Article).filter(Article.shop_id == shop_id) \
        .all()


# -------------------------------------------------------------------- #
# execution


def execute_actions(
    order: Order, payment_state: PaymentState, initiator_id: UserID
) -> None:
    """Execute relevant actions for this order in its new payment state."""
    article_numbers = {item.article_number for item in order.items}

    if not article_numbers:
        return

    quantities_by_article_number = {
        item.article_number: item.quantity for item in order.items
    }

    actions = _get_actions(article_numbers, payment_state)

    for action in actions:
        article_quantity = quantities_by_article_number[action.article_number]

        _execute_procedure(order, action, article_quantity, initiator_id)


def _get_actions(
    article_numbers: Set[ArticleNumber], payment_state: PaymentState
) -> Sequence[OrderAction]:
    """Return the order actions for those article numbers."""
    return OrderAction.query \
        .filter(OrderAction.article_number.in_(article_numbers)) \
        .filter_by(_payment_state=payment_state.name) \
        .all()


def _execute_procedure(
    order: Order,
    action: OrderAction,
    article_quantity: int,
    initiator_id: UserID,
) -> None:
    """Execute the procedure configured for that order action."""
    article_number = action.article_number
    procedure_name = action.procedure
    params = action.parameters

    procedure = _get_procedure(procedure_name, article_number)

    procedure(order, article_number, article_quantity, initiator_id, params)


def _get_procedure(name: str, article_number: ArticleNumber) -> OrderActionType:
    """Return procedure with that name, or raise an exception if the
    name is not registerd.
    """
    procedure = PROCEDURES_BY_NAME.get(name)

    if procedure is None:
        raise Exception(
            f"Unknown procedure '{name}' configured "
            f"for article number '{article_number}'."
        )

    return procedure
