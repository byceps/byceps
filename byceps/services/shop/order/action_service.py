"""
byceps.services.shop.order.action_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Callable, Optional, Sequence
from uuid import UUID

from ....database import db
from ....typing import UserID

from ..article.transfer.models import ArticleNumber

from .actions.award_badge import award_badge
from .actions.create_ticket_bundles import create_ticket_bundles
from .actions.create_tickets import create_tickets
from .actions.revoke_ticket_bundles import revoke_ticket_bundles
from .actions.revoke_tickets import revoke_tickets
from .dbmodels.order_action import OrderAction as DbOrderAction
from .transfer.action import Action, ActionParameters
from .transfer.order import Order, PaymentState


OrderActionType = Callable[
    [Order, ArticleNumber, int, UserID, ActionParameters], None
]


PROCEDURES_BY_NAME = {
    'award_badge': award_badge,
    'create_ticket_bundles': create_ticket_bundles,
    'revoke_ticket_bundles': revoke_ticket_bundles,
    'create_tickets': create_tickets,
    'revoke_tickets': revoke_tickets,
}


# -------------------------------------------------------------------- #
# creation/removal


def create_action(
    article_number: ArticleNumber,
    payment_state: PaymentState,
    procedure_name: str,
    parameters: ActionParameters,
) -> None:
    """Create an order action."""
    db_action = DbOrderAction(
        article_number, payment_state, procedure_name, parameters
    )

    db.session.add(db_action)
    db.session.commit()


def delete_action(action_id: UUID) -> None:
    """Delete the order action."""
    db.session.query(DbOrderAction) \
        .filter_by(id=action_id) \
        .delete()

    db.session.commit()


def delete_actions_for_article(article_number: ArticleNumber) -> None:
    """Delete all order actions for an article."""
    db.session.query(DbOrderAction) \
        .filter_by(article_number=article_number) \
        .delete()

    db.session.commit()


def find_action(action_id: UUID) -> Optional[Action]:
    """Return the action with that ID, if found."""
    db_action = db.session.get(DbOrderAction, action_id)

    if db_action is None:
        return None

    return _db_entity_to_action(db_action)


# -------------------------------------------------------------------- #
# retrieval


def get_actions_for_article(article_number: ArticleNumber) -> list[Action]:
    """Return the order actions defined for that article."""
    db_actions = db.session \
        .query(DbOrderAction) \
        .filter_by(article_number=article_number) \
        .all()

    return [_db_entity_to_action(db_action) for db_action in db_actions]


def _db_entity_to_action(db_action: DbOrderAction) -> Action:
    return Action(
        id=db_action.id,
        article_number=db_action.article_number,
        payment_state=db_action.payment_state,
        procedure_name=db_action.procedure,
        parameters=db_action.parameters,
    )


# -------------------------------------------------------------------- #
# execution


def execute_actions(
    order: Order, payment_state: PaymentState, initiator_id: UserID
) -> None:
    """Execute relevant actions for this order in its new payment state."""
    article_numbers = {
        line_item.article_number for line_item in order.line_items
    }

    if not article_numbers:
        return

    quantities_by_article_number = {
        line_item.article_number: line_item.quantity
        for line_item in order.line_items
    }

    actions = _get_actions(article_numbers, payment_state)

    for action in actions:
        article_quantity = quantities_by_article_number[action.article_number]

        _execute_procedure(order, action, article_quantity, initiator_id)


def _get_actions(
    article_numbers: set[ArticleNumber], payment_state: PaymentState
) -> Sequence[Action]:
    """Return the order actions for those article numbers."""
    db_actions = db.session \
        .query(DbOrderAction) \
        .filter(DbOrderAction.article_number.in_(article_numbers)) \
        .filter_by(_payment_state=payment_state.name) \
        .all()

    return [_db_entity_to_action(db_action) for db_action in db_actions]


def _execute_procedure(
    order: Order,
    action: Action,
    article_quantity: int,
    initiator_id: UserID,
) -> None:
    """Execute the procedure configured for that order action."""
    procedure = _get_procedure(action.procedure_name, action.article_number)

    procedure(
        order,
        action.article_number,
        article_quantity,
        initiator_id,
        action.parameters,
    )


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
