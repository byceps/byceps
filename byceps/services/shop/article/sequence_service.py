"""
byceps.services.shop.article.sequence_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional

from ..sequence import service as sequence_service
from ..sequence.transfer.models import NumberSequence, Purpose
from ..shop.transfer.models import ShopID

from .transfer.models import (
    ArticleNumber,
    ArticleNumberSequence,
    ArticleNumberSequenceID,
)


def create_article_number_sequence(
    shop_id: ShopID, prefix: str, *, value: Optional[int] = None
) -> ArticleNumberSequenceID:
    """Create an article number sequence."""
    return sequence_service.create_sequence(
        shop_id, Purpose.article, prefix, value=value
    )


def delete_article_number_sequence(
    sequence_id: ArticleNumberSequenceID,
) -> None:
    """Delete the article number sequence."""
    sequence_service.delete_sequence(sequence_id)


def find_article_number_sequence(
    sequence_id: ArticleNumberSequenceID,
) -> Optional[ArticleNumberSequence]:
    """Return the article number sequence, or `None` if the sequence ID
    is unknown or if the sequence's purpose is not article numbers.
    """
    sequence = sequence_service._find_sequence(sequence_id, Purpose.article)

    if sequence is None:
        return None

    return _to_article_number_sequence(sequence)


def find_article_number_sequences_for_shop(
    shop_id: ShopID,
) -> List[ArticleNumberSequence]:
    """Return the article number sequences defined for that shop."""
    sequences = sequence_service._find_number_sequences(
        shop_id, Purpose.article
    )

    return [_to_article_number_sequence(sequence) for sequence in sequences]


def generate_article_number(
    sequence_id: ArticleNumberSequenceID,
) -> ArticleNumber:
    """Generate and reserve an unused, unique article number from this
    sequence.
    """
    sequence = sequence_service._get_next_sequence_step(
        sequence_id, Purpose.article
    )
    return ArticleNumber(f'{sequence.prefix}{sequence.value:05d}')


def _to_article_number_sequence(
    sequence: NumberSequence,
) -> ArticleNumberSequence:
    return ArticleNumberSequence(
        sequence.id,
        sequence.shop_id,
        sequence.prefix,
        sequence.value,
    )
