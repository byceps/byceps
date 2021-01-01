"""
byceps.services.shop.order.sequence_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import List, Optional

from sqlalchemy.exc import IntegrityError

from ....database import db

from ..shop.transfer.models import ShopID

from .models.number_sequence import OrderNumberSequence as DbOrderNumberSequence
from .transfer.models import (
    OrderNumber,
    OrderNumberSequence,
    OrderNumberSequenceID,
)


def create_order_number_sequence(
    shop_id: ShopID, prefix: str, *, value: Optional[int] = None
) -> Optional[OrderNumberSequenceID]:
    """Create an order number sequence.

    Return the resulting sequence's ID, or `None` if the sequence could
    not be created.
    """
    sequence = DbOrderNumberSequence(shop_id, prefix, value=value)

    db.session.add(sequence)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return None

    return sequence.id


def delete_order_number_sequence(sequence_id: OrderNumberSequenceID) -> None:
    """Delete the order number sequence."""
    db.session.query(DbOrderNumberSequence) \
        .filter_by(id=sequence_id) \
        .delete()

    db.session.commit()


def find_order_number_sequence(
    sequence_id: OrderNumberSequenceID,
) -> Optional[OrderNumberSequence]:
    """Return the order number sequence, or `None` if the sequence ID
    is unknown.
    """
    sequence = DbOrderNumberSequence.query \
        .filter_by(id=sequence_id) \
        .one_or_none()

    if sequence is None:
        return None

    return _db_entity_to_order_number_sequence(sequence)


def find_order_number_sequences_for_shop(
    shop_id: ShopID,
) -> List[OrderNumberSequence]:
    """Return the order number sequences defined for that shop."""
    sequences = DbOrderNumberSequence.query \
        .filter_by(shop_id=shop_id) \
        .all()

    return [
        _db_entity_to_order_number_sequence(sequence) for sequence in sequences
    ]


class OrderNumberGenerationFailed(Exception):
    """Indicate that generating a prefixed, sequential order number has
    failed.
    """

    def __init__(self, message: str) -> None:
        self.message = message


def generate_order_number(sequence_id: OrderNumberSequenceID) -> OrderNumber:
    """Generate and reserve an unused, unique order number from this
    sequence.
    """
    sequence = DbOrderNumberSequence.query \
        .filter_by(id=sequence_id) \
        .with_for_update() \
        .one_or_none()

    if sequence is None:
        raise OrderNumberGenerationFailed(
            f'No order number sequence found for ID "{sequence_id}".'
        )

    sequence.value = DbOrderNumberSequence.value + 1
    db.session.commit()

    return OrderNumber(f'{sequence.prefix}{sequence.value:05d}')


def _db_entity_to_order_number_sequence(
    sequence: DbOrderNumberSequence,
) -> OrderNumberSequence:
    return OrderNumberSequence(
        sequence.id,
        sequence.shop_id,
        sequence.prefix,
        sequence.value,
    )
