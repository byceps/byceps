"""
byceps.services.shop.order.order_action_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from collections.abc import Iterator
from uuid import UUID

import structlog

from byceps.services.shop.product import product_service
from byceps.services.shop.product.models import ProductID, ProductType
from byceps.services.user.models import User
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from . import order_action_repository
from .actions import ticket as ticket_actions
from .actions import ticket_bundle as ticket_bundle_actions
from .actions import user_badge as user_badge_actions
from .dbmodels.order_action import DbOrderAction
from .errors import OrderActionFailedError
from .models.action import Action, ActionParameters, ActionProcedure
from .models.order import LineItem, Order, PaidOrder, PaymentState


log = structlog.get_logger()


_PROCEDURES_BY_NAME: dict[str, ActionProcedure] = {
    'award_badge': user_badge_actions.get_action_procedure(),
    'create_ticket_bundles': ticket_bundle_actions.get_action_procedure(),
    'create_tickets': ticket_actions.get_action_procedure(),
}

_PROCEDURES_BY_PRODUCT_TYPE: dict[ProductType, ActionProcedure] = {
    ProductType.ticket: ticket_actions.get_action_procedure(),
    ProductType.ticket_bundle: ticket_bundle_actions.get_action_procedure(),
}


# -------------------------------------------------------------------- #
# creation/removal


def create_action(
    product_id: ProductID, procedure_name: str, parameters: ActionParameters
) -> None:
    """Create an order action."""
    action_id = generate_uuid7()

    order_action_repository.create_action(
        action_id, product_id, procedure_name, parameters
    )


def delete_action(action_id: UUID) -> None:
    """Delete the order action."""
    order_action_repository.delete_action(action_id)


def delete_actions_for_product(product_id: ProductID) -> None:
    """Delete all order actions for a product."""
    order_action_repository.delete_actions_for_product(product_id)


def find_action(action_id: UUID) -> Action | None:
    """Return the action with that ID, if found."""
    db_action = order_action_repository.find_action(action_id)

    if db_action is None:
        return None

    return _db_entity_to_action(db_action)


# -------------------------------------------------------------------- #
# retrieval


def get_actions_for_product(product_id: ProductID) -> list[Action]:
    """Return the order actions defined for that product."""
    db_actions = order_action_repository.get_actions_for_product(product_id)

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


def execute_actions_on_payment(
    order: PaidOrder, initiator: User
) -> Result[None, OrderActionFailedError]:
    """Execute item creation actions for this order."""
    for line_item, actions in _get_line_items_with_actions(order):
        for action in actions:
            match _execute_action_on_payment(
                action, order, PaymentState.paid, line_item, initiator
            ):
                case Err(e):
                    return Err(e)

    return Ok(None)


def execute_actions_on_cancellation_before_payment(
    order: Order, initiator: User
) -> Result[None, OrderActionFailedError]:
    """Execute item revocation actions for this order."""
    for line_item, actions in _get_line_items_with_actions(order):
        for action in actions:
            match _execute_action_on_cancellation_before_payment(
                action,
                order,
                PaymentState.canceled_after_paid,
                line_item,
                initiator,
            ):
                case Err(e):
                    return Err(e)

    return Ok(None)


def execute_actions_on_cancellation_after_payment(
    order: Order, initiator: User
) -> Result[None, OrderActionFailedError]:
    """Execute item revocation actions for this order."""
    for line_item, actions in _get_line_items_with_actions(order):
        for action in actions:
            match _execute_action_on_cancellation_after_payment(
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
    db_actions = order_action_repository.get_actions_for_products(product_ids)

    return [_db_entity_to_action(db_action) for db_action in db_actions]


def _execute_action_on_payment(
    action: Action,
    order: PaidOrder,
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


def _execute_action_on_cancellation_before_payment(
    action: Action,
    order: Order,
    payment_state: PaymentState,
    line_item: LineItem,
    initiator: User,
) -> Result[None, OrderActionFailedError]:
    match _get_procedure(action.procedure_name, action.product_id):
        case Ok(procedure):
            match procedure.on_cancellation_before_payment(
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


def _execute_action_on_cancellation_after_payment(
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
    procedure = _PROCEDURES_BY_NAME.get(name)

    if procedure is None:
        product = product_service.get_product(product_id)
        return Err(
            OrderActionFailedError(
                f"Unknown procedure '{name}' configured "
                f"for product number '{product.item_number}'."
            )
        )

    return Ok(procedure)


def find_procedure_for_product_type(
    product_type: ProductType,
) -> ActionProcedure | None:
    """Find the action procedure for the product type."""
    return _PROCEDURES_BY_PRODUCT_TYPE.get(product_type)
