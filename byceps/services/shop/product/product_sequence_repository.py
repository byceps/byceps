"""
byceps.services.shop.product.product_sequence_repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError

from byceps.database import db
from byceps.services.shop.shop.models import ShopID
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid7

from .dbmodels.number_sequence import DbProductNumberSequence
from .models import ProductNumberSequenceID


def create_product_number_sequence(
    shop_id: ShopID, prefix: str, value: int
) -> Result[DbProductNumberSequence, None]:
    """Create a product number sequence."""
    sequence_id = ProductNumberSequenceID(generate_uuid7())

    db_sequence = DbProductNumberSequence(sequence_id, shop_id, prefix, value)

    db.session.add(db_sequence)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return Err(None)

    return Ok(db_sequence)


def delete_product_number_sequence(
    sequence_id: ProductNumberSequenceID,
) -> None:
    """Delete the product number sequence."""
    db.session.execute(
        delete(DbProductNumberSequence).filter_by(id=sequence_id)
    )
    db.session.commit()


def find_product_number_sequence(
    sequence_id: ProductNumberSequenceID,
) -> DbProductNumberSequence | None:
    """Return the product number sequence, if found."""
    return db.session.get(DbProductNumberSequence, sequence_id)


def get_product_number_sequences_for_shop(
    shop_id: ShopID,
) -> Sequence[DbProductNumberSequence]:
    """Return the product number sequences defined for that shop."""
    return db.session.scalars(
        select(DbProductNumberSequence).filter_by(shop_id=shop_id)
    ).all()


def generate_product_number(
    sequence_id: ProductNumberSequenceID,
) -> Result[tuple[str, int], str]:
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

    return Ok((prefix, value))
