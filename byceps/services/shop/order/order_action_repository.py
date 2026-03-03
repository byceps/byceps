"""
byceps.services.shop.order.order_action_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, select

from byceps.database import db
from byceps.services.shop.product.models import ProductID

from .dbmodels.order_action import DbOrderAction
from .models.action import ActionParameters


def create_action(
    action_id: UUID,
    product_id: ProductID,
    procedure_name: str,
    parameters: ActionParameters,
) -> None:
    """Create an order action."""
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


def find_action(action_id: UUID) -> DbOrderAction | None:
    """Return the action with that ID, if found."""
    return db.session.get(DbOrderAction, action_id)


def get_actions_for_product(product_id: ProductID) -> Sequence[DbOrderAction]:
    """Return the order actions defined for that product."""
    return db.session.scalars(
        select(DbOrderAction).filter_by(product_id=product_id)
    ).all()


def get_actions_for_products(
    product_ids: set[ProductID],
) -> Sequence[DbOrderAction]:
    """Return the order actions for those product IDs."""
    if not product_ids:
        return []

    return db.session.scalars(
        select(DbOrderAction).filter(DbOrderAction.product_id.in_(product_ids))
    ).all()
