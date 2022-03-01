"""
byceps.services.shop.article.sequence_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from typing import Optional

from sqlalchemy.exc import IntegrityError

from ....database import db

from ..shop.transfer.models import ShopID

from .dbmodels.number_sequence import (
    ArticleNumberSequence as DbArticleNumberSequence,
)
from .transfer.models import (
    ArticleNumber,
    ArticleNumberSequence,
    ArticleNumberSequenceID,
)


class ArticleNumberSequenceCreationFailed(Exception):
    pass


def create_article_number_sequence(
    shop_id: ShopID, prefix: str, *, value: Optional[int] = None
) -> ArticleNumberSequence:
    """Create an article number sequence."""
    db_sequence = DbArticleNumberSequence(shop_id, prefix, value=value)

    db.session.add(db_sequence)

    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        raise ArticleNumberSequenceCreationFailed(
            f'Could not sequence with prefix "{prefix}"'
        ) from exc

    return _db_entity_to_article_number_sequence(db_sequence)


def delete_article_number_sequence(
    sequence_id: ArticleNumberSequenceID,
) -> None:
    """Delete the article number sequence."""
    db.session.query(DbArticleNumberSequence) \
        .filter_by(id=sequence_id) \
        .delete()

    db.session.commit()


def get_article_number_sequence(
    sequence_id: ArticleNumberSequenceID,
) -> ArticleNumberSequence:
    """Return the article number sequence, or raise an exception."""
    db_sequence = db.session \
        .query(DbArticleNumberSequence) \
        .filter_by(id=sequence_id) \
        .one_or_none()

    if db_sequence is None:
        raise ValueError(f'Unknown article number sequence ID "{sequence_id}"')

    return _db_entity_to_article_number_sequence(db_sequence)


def get_article_number_sequences_for_shop(
    shop_id: ShopID,
) -> list[ArticleNumberSequence]:
    """Return the article number sequences defined for that shop."""
    db_sequences = db.session \
        .query(DbArticleNumberSequence) \
        .filter_by(shop_id=shop_id) \
        .all()

    return [
        _db_entity_to_article_number_sequence(db_sequence)
        for db_sequence in db_sequences
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
    db_sequence = db.session \
        .query(DbArticleNumberSequence) \
        .filter_by(id=sequence_id) \
        .with_for_update() \
        .one_or_none()

    if db_sequence is None:
        raise ArticleNumberGenerationFailed(
            f'No article number sequence found for ID "{sequence_id}".'
        )

    db_sequence.value = DbArticleNumberSequence.value + 1
    db.session.commit()

    return ArticleNumber(f'{db_sequence.prefix}{db_sequence.value:05d}')


def _db_entity_to_article_number_sequence(
    db_sequence: DbArticleNumberSequence,
) -> ArticleNumberSequence:
    return ArticleNumberSequence(
        id=db_sequence.id,
        shop_id=db_sequence.shop_id,
        prefix=db_sequence.prefix,
        value=db_sequence.value,
    )
