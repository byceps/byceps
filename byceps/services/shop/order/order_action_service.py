"""
byceps.services.shop.order.order_action_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from collections.abc import Iterator
from uuid import UUID

from sqlalchemy import delete, select
import structlog

from byceps.database import db
from byceps.services.shop.product import product_service
from byceps.services.shop.product.models import ProductID
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .actions import create_ticket_bundles
from .actions import create_tickets
from .actions import revoke_ticket_bundles
from .actions import revoke_tickets
from .actions import user_badge as user_badge_actions
from .dbmodels.order_action import DbOrderAction
from .errors import OrderActionFailedError
from .models.action import Action, ActionParameters, ActionProcedure
from .models.order import LineItem, Order, PaymentState


log = structlog.get_logger()


PROCEDURES_BY_NAME: dict[str, ActionProcedure] = {
    'award_badge': ActionProcedure(
        on_payment=user_badge_actions.on_payment,
        on_cancellation_after_payment=user_badge_actions.on_cancellation_after_payment,
    ),
    'create_ticket_bundles': ActionProcedure(
        on_payment=create_ticket_bundles.on_payment,
        on_cancellation_after_payment=revoke_ticket_bundles.on_cancellation_after_payment,
    ),
    'create_tickets': ActionProcedure(
        on_payment=create_tickets.on_payment,
        on_cancellation_after_payment=revoke_tickets.on_cancellation_after_payment,
    ),
}


# -------------------------------------------------------------------- #
# creation/removal


def create_action(
    product_id: ProductID, procedure_name: str, parameters: ActionParameters
) -> None:
    """Create an order action."""
    action_id = generate_uuid7()

    db_action = DbOrderAction(action_id, product_id, procedure_name, parameters)

    db.session.add(db_action)
    db.session.commit()


def delete_action(action_id: UUID) -> None:
    """Delete the order action."""
    db.session.execute(delete(DbOrderAction).filter_by(id=action_id))
    db.session.commit()


def delete_actions_for_product(product_id: ProductID) -> None:
    """Delete all order actions for a product."""
    db.session.execute(delete(DbOrderAction).filter_by(product_id=product_id))
    db.session.commit()


def find_action(action_id: UUID) -> Action | None:
    """Return the action with that ID, if found."""
    db_action = db.session.get(DbOrderAction, action_id)

    if db_action is None:
        return None

    return _db_entity_to_action(db_action)


# -------------------------------------------------------------------- #
# retrieval


def get_actions_for_product(product_id: ProductID) -> list[Action]:
    """Return the order actions defined for that product."""
    db_actions = db.session.scalars(
        select(DbOrderAction).filter_by(product_id=product_id)
    ).all()

    return [_db_entity_to_action(db_action) for db_action in db_actions]


def _db_entity_to_action(db_action: DbOrderAction) -> Action:
    return Action(
        id=db_action.id,
        product_id=db_action.product_id,
        procedure_name=db_action.procedure,
        parameters=db_action.parameters,
    )


# -------------------------------------------------------------------- #
# execution


def execute_creation_actions(
    order: Order, initiator: User
) -> Result[None, OrderActionFailedError]:
    """Execute item creation actions for this order."""
    for line_item, actions in _get_line_items_with_actions(order):
        for action in actions:
            match _execute_creation_action(
                action, order, PaymentState.paid, line_item, initiator
            ):
                case Err(e):
                    return Err(e)

    return Ok(None)


def execute_revocation_actions(
    order: Order, initiator: User
) -> Result[None, OrderActionFailedError]:
    """Execute item revocation actions for this order."""
    for line_item, actions in _get_line_items_with_actions(order):
        for action in actions:
            match _execute_revocation_action(
                action,
                order,
                PaymentState.canceled_after_paid,
                line_item,
                initiator,
            ):
                case Err(e):
                    return Err(e)

    return Ok(None)


def _get_line_items_with_actions(
    order: Order,
) -> Iterator[tuple[LineItem, list[Action]]]:
    product_ids = {line_item.product_id for line_item in order.line_items}

    actions_by_product_id: dict[ProductID, list[Action]] = defaultdict(list)
    for action in _get_actions(product_ids):
        actions_by_product_id[action.product_id].append(action)

    for line_item in order.line_items:
        actions = actions_by_product_id.get(line_item.product_id)
        if actions:
            yield line_item, actions


def _get_actions(product_ids: set[ProductID]) -> list[Action]:
    """Return the order actions for those product IDs."""
    if not product_ids:
        return []

    db_actions = db.session.scalars(
        select(DbOrderAction).filter(DbOrderAction.product_id.in_(product_ids))
    ).all()

    return [_db_entity_to_action(db_action) for db_action in db_actions]


def _execute_creation_action(
    action: Action,
    order: Order,
    payment_state: PaymentState,
    line_item: LineItem,
    initiator: User,
) -> Result[None, OrderActionFailedError]:
    match _get_procedure(action.procedure_name, action.product_id):
        case Ok(procedure):
            match procedure.on_payment(
                order, line_item, initiator, action.parameters
            ):
                case Ok(_):
                    return Ok(None)
                case Err(e):
                    log.error(
                        'Order action execution failed',
                        order_id=str(order.id),
                        order_number=order.order_number,
                        payment_state=payment_state.name,
                        initiator=initiator.screen_name,
                        error_details=e.details,
                    )
                    return Err(e)
        case Err(e):
            log.error(
                'Unknown order action configured',
                order_id=str(order.id),
                order_number=order.order_number,
                payment_state=payment_state.name,
                initiator=initiator.screen_name,
                error_details=e.details,
            )
            return Err(e)


def _execute_revocation_action(
    action: Action,
    order: Order,
    payment_state: PaymentState,
    line_item: LineItem,
    initiator: User,
) -> Result[None, OrderActionFailedError]:
    match _get_procedure(action.procedure_name, action.product_id):
        case Ok(procedure):
            match procedure.on_cancellation_after_payment(
                order, line_item, initiator, action.parameters
            ):
                case Ok(_):
                    return Ok(None)
                case Err(e):
                    log.error(
                        'Order action execution failed',
                        order_id=str(order.id),
                        order_number=order.order_number,
                        payment_state=payment_state.name,
                        initiator=initiator.screen_name,
                        error_details=e.details,
                    )
                    return Err(e)
        case Err(e):
            log.error(
                'Unknown order action configured',
                order_id=str(order.id),
                order_number=order.order_number,
                payment_state=payment_state.name,
                initiator=initiator.screen_name,
                error_details=e.details,
            )
            return Err(e)


def _get_procedure(
    name: str, product_id: ProductID
) -> Result[ActionProcedure, OrderActionFailedError]:
    """Return the procedure with that name, or an error if the name is
    not registered.
    """
    procedure = PROCEDURES_BY_NAME.get(name)

    if procedure is None:
        product = product_service.get_product(product_id)
        return Err(
            OrderActionFailedError(
                f"Unknown procedure '{name}' configured "
                f"for product number '{product.item_number}'."
            )
        )

    return Ok(procedure)
