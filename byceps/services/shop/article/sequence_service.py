"""
byceps.services.shop.article.sequence_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import List, Optional

from sqlalchemy.exc import IntegrityError

from ....database import db

from ..shop.transfer.models import ShopID

from .dbmodels.number_sequence import ArticleNumberSequence as DbArticleNumberSequence
from .transfer.models import (
    ArticleNumber,
    ArticleNumberSequence,
    ArticleNumberSequenceID,
)


def create_article_number_sequence(
    shop_id: ShopID, prefix: str, *, value: Optional[int] = None
) -> Optional[ArticleNumberSequenceID]:
    """Create an article number sequence.

    Return the resulting sequence's ID, or `None` if the sequence could
    not be created.
    """
    sequence = DbArticleNumberSequence(shop_id, prefix, value=value)

    db.session.add(sequence)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return None

    return sequence.id


def delete_article_number_sequence(
    sequence_id: ArticleNumberSequenceID,
) -> None:
    """Delete the article number sequence."""
    db.session.query(DbArticleNumberSequence) \
        .filter_by(id=sequence_id) \
        .delete()

    db.session.commit()


def find_article_number_sequence(
    sequence_id: ArticleNumberSequenceID,
) -> Optional[ArticleNumberSequence]:
    """Return the article number sequence, or `None` if the sequence ID
    is unknown.
    """
    sequence = DbArticleNumberSequence.query \
        .filter_by(id=sequence_id) \
        .one_or_none()

    if sequence is None:
        return None

    return _db_entity_to_article_number_sequence(sequence)


def find_article_number_sequences_for_shop(
    shop_id: ShopID,
) -> List[ArticleNumberSequence]:
    """Return the article number sequences defined for that shop."""
    sequences = DbArticleNumberSequence.query \
        .filter_by(shop_id=shop_id) \
        .all()

    return [
        _db_entity_to_article_number_sequence(sequence)
        for sequence in sequences
    ]


class ArticleNumberGenerationFailed(Exception):
    """Indicate that generating a prefixed, sequential article number
    has failed.
    """

    def __init__(self, message: str) -> None:
        self.message = message


def generate_article_number(
    sequence_id: ArticleNumberSequenceID,
) -> ArticleNumber:
    """Generate and reserve the next article number from this sequence."""
    sequence = DbArticleNumberSequence.query \
        .filter_by(id=sequence_id) \
        .with_for_update() \
        .one_or_none()

    if sequence is None:
        raise ArticleNumberGenerationFailed(
            f'No article number sequence found for ID "{sequence_id}".'
        )

    sequence.value = DbArticleNumberSequence.value + 1
    db.session.commit()

    return ArticleNumber(f'{sequence.prefix}{sequence.value:05d}')


def _db_entity_to_article_number_sequence(
    sequence: DbArticleNumberSequence,
) -> ArticleNumberSequence:
    return ArticleNumberSequence(
        sequence.id,
        sequence.shop_id,
        sequence.prefix,
        sequence.value,
    )
