"""
byceps.services.shop.order.order_sequence_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError

from byceps.database import db
from byceps.services.shop.shop.models import ShopID
from byceps.util.result import Err, Ok, Result

from .dbmodels.number_sequence import DbOrderNumberSequence
from .models.number import (
    OrderNumber,
    OrderNumberSequence,
    OrderNumberSequenceID,
)


def create_order_number_sequence(
    shop_id: ShopID, prefix: str, *, value: int | None = None
) -> Result[OrderNumberSequence, None]:
    """Create an order number sequence."""
    db_sequence = DbOrderNumberSequence(shop_id, prefix, value=value)

    db.session.add(db_sequence)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return Err(None)

    sequence = _db_entity_to_order_number_sequence(db_sequence)

    return Ok(sequence)


def delete_order_number_sequence(sequence_id: OrderNumberSequenceID) -> None:
    """Delete the order number sequence."""
    db.session.execute(delete(DbOrderNumberSequence).filter_by(id=sequence_id))
    db.session.commit()


def get_order_number_sequence(
    sequence_id: OrderNumberSequenceID,
) -> OrderNumberSequence:
    """Return the order number sequence, or raise an exception."""
    db_sequence = db.session.get(DbOrderNumberSequence, sequence_id)

    if db_sequence is None:
        raise ValueError(f'Unknown order number sequence ID "{sequence_id}"')

    return _db_entity_to_order_number_sequence(db_sequence)


def get_order_number_sequences_for_shop(
    shop_id: ShopID,
) -> list[OrderNumberSequence]:
    """Return the order number sequences defined for that shop."""
    db_sequences = db.session.scalars(
        select(DbOrderNumberSequence).filter_by(shop_id=shop_id)
    ).all()

    return [
        _db_entity_to_order_number_sequence(db_sequence)
        for db_sequence in db_sequences
    ]


def generate_order_number(
    sequence_id: OrderNumberSequenceID,
) -> Result[OrderNumber, str]:
    """Generate and reserve an unused, unique order number from this
    sequence.
    """
    row = db.session.execute(
        update(DbOrderNumberSequence)
        .filter_by(id=sequence_id)
        .values(value=DbOrderNumberSequence.value + 1)
        .returning(DbOrderNumberSequence.prefix, DbOrderNumberSequence.value)
    ).one_or_none()
    db.session.commit()

    if row is None:
        return Err(f'No order number sequence found for ID "{sequence_id}".')

    prefix, value = row
    order_number = OrderNumber(f'{prefix}{value:05d}')

    return Ok(order_number)


def _db_entity_to_order_number_sequence(
    db_sequence: DbOrderNumberSequence,
) -> OrderNumberSequence:
    return OrderNumberSequence(
        id=db_sequence.id,
        shop_id=db_sequence.shop_id,
        prefix=db_sequence.prefix,
        value=db_sequence.value,
    )
