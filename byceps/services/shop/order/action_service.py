"""
byceps.services.shop.order.action_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Any, Callable, Dict, Optional

from ....database import db

from ..article.models.article import ArticleNumber

from .actions.award_badge import award_badge
from .models.order import Order, OrderID
from .models.order_action import OrderAction
from . import service as order_service


Parameters = Dict[str, Any]

OrderActionType = Callable[[Order, ArticleNumber, Parameters], None]


def create_order_action(article_number: ArticleNumber, procedure: str,
                        parameters: Dict[str, Any]) -> None:
    """Create an order action."""
    action = OrderAction(article_number, procedure, parameters)

    db.session.add(action)
    db.session.commit()


def execute_order_actions(order_id: OrderID) -> None:
    """Execute relevant actions for order."""
    order = order_service.find_order_with_details(order_id)

    article_numbers = {item.article_number for item in order.items}

    if not article_numbers:
        return

    actions = OrderAction.query \
        .filter(OrderAction.article_number.in_(article_numbers)) \
        .all()

    for action in actions:
        article_number = action.article_number
        procedure_name = action.procedure
        params = action.parameters

        procedure = find_procedure(procedure_name)

        procedure(order, article_number, params)


def find_procedure(name: str) -> Optional[OrderActionType]:
    procedures_by_name = {
        'award_badge': award_badge,
    }  # type: Dict[str, OrderActionType]

    return procedures_by_name.get(name)
