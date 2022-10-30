"""
byceps.services.shop.order.order_action_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Callable, Optional, Sequence
from uuid import UUID

from sqlalchemy import delete, select

from ....database import db
from ....typing import UserID

from ..article import article_service
from ..article.transfer.models import ArticleID

from .actions.award_badge import award_badge
from .actions.create_ticket_bundles import create_ticket_bundles
from .actions.create_tickets import create_tickets
from .actions.revoke_ticket_bundles import revoke_ticket_bundles
from .actions.revoke_tickets import revoke_tickets
from .dbmodels.order_action import DbOrderAction
from .transfer.action import Action, ActionParameters
from .transfer.order import LineItem, Order, PaymentState


OrderActionType = Callable[[Order, LineItem, UserID, ActionParameters], None]


PROCEDURES_BY_NAME: dict[str, OrderActionType] = {
    'award_badge': award_badge,
    'create_ticket_bundles': create_ticket_bundles,
    'revoke_ticket_bundles': revoke_ticket_bundles,
    'create_tickets': create_tickets,
    'revoke_tickets': revoke_tickets,
}


# -------------------------------------------------------------------- #
# creation/removal


def create_action(
    article_id: ArticleID,
    payment_state: PaymentState,
    procedure_name: str,
    parameters: ActionParameters,
) -> None:
    """Create an order action."""
    db_action = DbOrderAction(
        article_id, payment_state, procedure_name, parameters
    )

    db.session.add(db_action)
    db.session.commit()


def delete_action(action_id: UUID) -> None:
    """Delete the order action."""
    db.session.execute(delete(DbOrderAction).filter_by(id=action_id))
    db.session.commit()


def delete_actions_for_article(article_id: ArticleID) -> None:
    """Delete all order actions for an article."""
    db.session.execute(delete(DbOrderAction).filter_by(article_id=article_id))
    db.session.commit()


def find_action(action_id: UUID) -> Optional[Action]:
    """Return the action with that ID, if found."""
    db_action = db.session.get(DbOrderAction, action_id)

    if db_action is None:
        return None

    return _db_entity_to_action(db_action)


# -------------------------------------------------------------------- #
# retrieval


def get_actions_for_article(article_id: ArticleID) -> list[Action]:
    """Return the order actions defined for that article."""
    db_actions = db.session.scalars(
        select(DbOrderAction).filter_by(article_id=article_id)
    ).all()

    return [_db_entity_to_action(db_action) for db_action in db_actions]


def _db_entity_to_action(db_action: DbOrderAction) -> Action:
    return Action(
        id=db_action.id,
        article_id=db_action.article_id,
        payment_state=db_action.payment_state,
        procedure_name=db_action.procedure,
        parameters=db_action.parameters,
    )


# -------------------------------------------------------------------- #
# execution


def execute_creation_actions(order: Order, initiator_id: UserID) -> None:
    """Execute item creation actions for this order."""
    _execute_actions(order, PaymentState.paid, initiator_id)


def execute_revocation_actions(order: Order, initiator_id: UserID) -> None:
    """Execute item revocation actions for this order."""
    _execute_actions(order, PaymentState.canceled_after_paid, initiator_id)


def _execute_actions(
    order: Order, payment_state: PaymentState, initiator_id: UserID
) -> None:
    """Execute relevant actions for this order in its new payment state."""
    article_ids = {line_item.article_id for line_item in order.line_items}

    actions = _get_actions(article_ids, payment_state)
    actions_by_article_id = {action.article_id: action for action in actions}

    for line_item in order.line_items:
        action = actions_by_article_id.get(line_item.article_id)
        if action is None:
            continue

        procedure = _get_procedure(action.procedure_name, action.article_id)
        procedure(order, line_item, initiator_id, action.parameters)


def _get_actions(
    article_ids: set[ArticleID], payment_state: PaymentState
) -> Sequence[Action]:
    """Return the order actions for those article IDs."""
    if not article_ids:
        return []

    db_actions = db.session.scalars(
        select(DbOrderAction)
        .filter(DbOrderAction.article_id.in_(article_ids))
        .filter_by(_payment_state=payment_state.name)
    ).all()

    return [_db_entity_to_action(db_action) for db_action in db_actions]


def _get_procedure(name: str, article_id: ArticleID) -> OrderActionType:
    """Return procedure with that name, or raise an exception if the
    name is not registerd.
    """
    procedure = PROCEDURES_BY_NAME.get(name)

    if procedure is None:
        article = article_service.get_article(article_id)
        raise Exception(
            f"Unknown procedure '{name}' configured "
            f"for article number '{article.item_number}'."
        )

    return procedure
