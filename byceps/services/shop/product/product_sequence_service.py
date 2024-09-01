"""
byceps.services.shop.product.product_sequence_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError

from byceps.database import db
from byceps.services.shop.shop.models import ShopID
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .dbmodels.number_sequence import DbProductNumberSequence
from .models import (
    ProductNumber,
    ProductNumberSequence,
    ProductNumberSequenceID,
)


def create_product_number_sequence(
    shop_id: ShopID, prefix: str, *, value: int = 0
) -> Result[ProductNumberSequence, None]:
    """Create a product number sequence."""
    sequence_id = ProductNumberSequenceID(generate_uuid7())

    db_sequence = DbProductNumberSequence(sequence_id, shop_id, prefix, value)

    db.session.add(db_sequence)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return Err(None)

    sequence = _db_entity_to_product_number_sequence(db_sequence)

    return Ok(sequence)


def delete_product_number_sequence(
    sequence_id: ProductNumberSequenceID,
) -> None:
    """Delete the product number sequence."""
    db.session.execute(
        delete(DbProductNumberSequence).filter_by(id=sequence_id)
    )
    db.session.commit()


def get_product_number_sequence(
    sequence_id: ProductNumberSequenceID,
) -> ProductNumberSequence:
    """Return the product number sequence, or raise an exception."""
    db_sequence = db.session.get(DbProductNumberSequence, sequence_id)

    if db_sequence is None:
        raise ValueError(f'Unknown product number sequence ID "{sequence_id}"')

    return _db_entity_to_product_number_sequence(db_sequence)


def get_product_number_sequences_for_shop(
    shop_id: ShopID,
) -> list[ProductNumberSequence]:
    """Return the product number sequences defined for that shop."""
    db_sequences = db.session.scalars(
        select(DbProductNumberSequence).filter_by(shop_id=shop_id)
    ).all()

    return [
        _db_entity_to_product_number_sequence(db_sequence)
        for db_sequence in db_sequences
    ]


def generate_product_number(
    sequence_id: ProductNumberSequenceID,
) -> Result[ProductNumber, str]:
    """Generate and reserve the next product number from this sequence."""
    row = db.session.execute(
        update(DbProductNumberSequence)
        .filter_by(id=sequence_id)
        .values(value=DbProductNumberSequence.value + 1)
        .returning(
            DbProductNumberSequence.prefix, DbProductNumberSequence.value
        )
    ).one_or_none()
    db.session.commit()

    if row is None:
        return Err(f'No product number sequence found for ID "{sequence_id}".')

    prefix, value = row
    product_number = ProductNumber(f'{prefix}{value:05d}')

    return Ok(product_number)


def _db_entity_to_product_number_sequence(
    db_sequence: DbProductNumberSequence,
) -> ProductNumberSequence:
    return ProductNumberSequence(
        id=db_sequence.id,
        shop_id=db_sequence.shop_id,
        prefix=db_sequence.prefix,
        value=db_sequence.value,
        archived=db_sequence.archived,
    )
