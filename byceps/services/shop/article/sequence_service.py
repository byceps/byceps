"""
byceps.services.shop.article.sequence_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional

from ..sequence import service as sequence_service
from ..sequence.transfer.models import NumberSequence, NumberSequenceID, Purpose
from ..shop.transfer.models import ShopID

from .transfer.models import ArticleNumber


def create_article_number_sequence(
    shop_id: ShopID, prefix: str, *, value: Optional[int] = None
) -> NumberSequenceID:
    """Create an article number sequence."""
    return sequence_service.create_sequence(
        shop_id, Purpose.article, prefix, value=value
    )


def delete_article_number_sequence(sequence_id: NumberSequenceID) -> None:
    """Delete the article number sequence."""
    sequence_service.delete_sequence(sequence_id)


def find_article_number_sequence(
    sequence_id: NumberSequenceID,
) -> Optional[NumberSequence]:
    """Return the article number sequence, or `None` if the sequence ID
    is unknown or if the sequence's purpose is not article numbers.
    """
    return sequence_service._find_sequence(sequence_id, Purpose.article)


def find_article_number_sequences_for_shop(
    shop_id: ShopID,
) -> List[NumberSequence]:
    """Return the article number sequences defined for that shop."""
    return sequence_service._find_number_sequences(shop_id, Purpose.article)


def generate_article_number(sequence_id: NumberSequenceID) -> ArticleNumber:
    """Generate and reserve an unused, unique article number from this
    sequence.
    """
    sequence = sequence_service._get_next_sequence_step(
        sequence_id, Purpose.article
    )
    return ArticleNumber(f'{sequence.prefix}{sequence.value:05d}')
