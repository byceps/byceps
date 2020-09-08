"""
byceps.services.shop.order.sequence_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional

from ....database import db

from ..sequence.models import NumberSequence as DbNumberSequence
from ..sequence.transfer.models import Purpose
from ..shop.transfer.models import ShopID

from .transfer.models import (
    OrderNumber,
    OrderNumberSequence,
    OrderNumberSequenceID,
)


def create_order_number_sequence(
    shop_id: ShopID, prefix: str, *, value: Optional[int] = None
) -> OrderNumberSequenceID:
    """Create an order number sequence."""
    sequence = DbNumberSequence(shop_id, Purpose.order, prefix, value=value)

    db.session.add(sequence)
    db.session.commit()

    return sequence.id


def delete_order_number_sequence(sequence_id: OrderNumberSequenceID) -> None:
    """Delete the order number sequence."""
    db.session.query(DbNumberSequence) \
        .filter_by(id=sequence_id) \
        .delete()

    db.session.commit()


def find_order_number_sequence(
    sequence_id: OrderNumberSequenceID,
) -> Optional[OrderNumberSequence]:
    """Return the order number sequence, or `None` if the sequence ID
    is unknown or if the sequence's purpose is not order numbers.
    """
    sequence = DbNumberSequence.query \
        .filter_by(id=sequence_id) \
        .filter_by(_purpose=Purpose.order.name) \
        .one_or_none()

    if sequence is None:
        return None

    return _db_entity_to_order_number_sequence(sequence)


def find_order_number_sequences_for_shop(
    shop_id: ShopID,
) -> List[OrderNumberSequence]:
    """Return the order number sequences defined for that shop."""
    sequences = DbNumberSequence.query \
        .filter_by(shop_id=shop_id) \
        .filter_by(_purpose=Purpose.order.name) \
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
    sequence = DbNumberSequence.query \
        .filter_by(id=sequence_id) \
        .filter_by(_purpose=Purpose.order.name) \
        .with_for_update() \
        .one_or_none()

    if sequence is None:
        raise OrderNumberGenerationFailed(
            f'No order number sequence found for ID "{sequence_id}".'
        )

    sequence.value = DbNumberSequence.value + 1
    db.session.commit()

    return OrderNumber(f'{sequence.prefix}{sequence.value:05d}')


def _db_entity_to_order_number_sequence(
    sequence: DbNumberSequence,
) -> OrderNumberSequence:
    return OrderNumberSequence(
        sequence.id,
        sequence.shop_id,
        sequence.prefix,
        sequence.value,
    )
