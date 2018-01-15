"""
byceps.services.shop.order.action_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Callable, Dict, Sequence, Set

from ....database import db

from ..article.models.article import ArticleNumber

from .actions.award_badge import award_badge
from .actions.create_ticket_bundles import create_ticket_bundles
from .actions.create_tickets import create_tickets
from .actions.revoke_tickets import revoke_tickets
from .models.order import OrderTuple
from .models.order_action import OrderAction, Parameters
from .models.payment import PaymentState


OrderActionType = Callable[[OrderTuple, ArticleNumber, int, Parameters], None]


PROCEDURES_BY_NAME = {
    'award_badge': award_badge,
    'create_ticket_bundles': create_ticket_bundles,
    'create_tickets': create_tickets,
    'revoke_tickets': revoke_tickets,
}  # type: Dict[str, OrderActionType]


# -------------------------------------------------------------------- #
# creation


def create_action(article_number: ArticleNumber, payment_state: PaymentState,
                  procedure: str, parameters: Parameters) -> None:
    """Create an order action."""
    action = OrderAction(article_number, payment_state, procedure, parameters)

    db.session.add(action)
    db.session.commit()


# -------------------------------------------------------------------- #
# execution

def execute_actions(order: OrderTuple, payment_state: PaymentState) -> None:
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

        _execute_procedure(order, action, article_quantity)


def _get_actions(article_numbers: Set[ArticleNumber],
                 payment_state: PaymentState) -> Sequence[OrderAction]:
    """Return the order actions for those article numbers."""
    return OrderAction.query \
        .filter(OrderAction.article_number.in_(article_numbers)) \
        .filter_by(_payment_state=payment_state.name) \
        .all()


def _execute_procedure(order: OrderTuple, action: OrderAction,
                       article_quantity: int) -> None:
    """Execute the procedure configured for that order action."""
    article_number = action.article_number
    procedure_name = action.procedure
    params = action.parameters

    procedure = _get_procedure(procedure_name, article_number)

    procedure(order, article_number, article_quantity, params)


def _get_procedure(name: str, article_number: ArticleNumber) -> OrderActionType:
    """Return procedure with that name, or raise an exception if the
    name is not registerd.
    """
    procedure = PROCEDURES_BY_NAME.get(name)

    if procedure is None:
        raise Exception(
            "Unknown procedure '{}' configured for article number '{}'."
                .format(name, article_number))

    return procedure
