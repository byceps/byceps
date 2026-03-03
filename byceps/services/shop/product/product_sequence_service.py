"""
byceps.services.shop.product.product_sequence_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.shop.shop.models import ShopID
from byceps.util.result import Err, Ok, Result

from . import product_sequence_repository
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
    match product_sequence_repository.create_product_number_sequence(
        shop_id, prefix, value
    ):
        case Ok(db_sequence):
            sequence = _db_entity_to_product_number_sequence(db_sequence)
            return Ok(sequence)
        case Err(e):
            return Err(e)


def delete_product_number_sequence(
    sequence_id: ProductNumberSequenceID,
) -> None:
    """Delete the product number sequence."""
    product_sequence_repository.delete_product_number_sequence(sequence_id)


def get_product_number_sequence(
    sequence_id: ProductNumberSequenceID,
) -> ProductNumberSequence:
    """Return the product number sequence, or raise an exception."""
    db_sequence = product_sequence_repository.find_product_number_sequence(
        sequence_id
    )

    if db_sequence is None:
        raise ValueError(f'Unknown product number sequence ID "{sequence_id}"')

    return _db_entity_to_product_number_sequence(db_sequence)


def get_product_number_sequences_for_shop(
    shop_id: ShopID,
) -> list[ProductNumberSequence]:
    """Return the product number sequences defined for that shop."""
    db_sequences = (
        product_sequence_repository.get_product_number_sequences_for_shop(
            shop_id
        )
    )

    return [
        _db_entity_to_product_number_sequence(db_sequence)
        for db_sequence in db_sequences
    ]


def generate_product_number(
    sequence_id: ProductNumberSequenceID,
) -> Result[ProductNumber, str]:
    """Generate and reserve the next product number from this sequence."""
    match product_sequence_repository.generate_product_number(sequence_id):
        case Ok(prefix_and_value):
            prefix, value = prefix_and_value
            product_number = ProductNumber(f'{prefix}{value:05d}')
            return Ok(product_number)
        case Err(e):
            return Err(e)


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
