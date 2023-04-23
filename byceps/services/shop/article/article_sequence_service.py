"""
byceps.services.shop.article.article_sequence_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from byceps.database import db
from byceps.services.shop.shop.models import ShopID
from byceps.util.result import Err, Ok, Result

from .dbmodels.number_sequence import DbArticleNumberSequence
from .models import (
    ArticleNumber,
    ArticleNumberSequence,
    ArticleNumberSequenceID,
)


def create_article_number_sequence(
    shop_id: ShopID, prefix: str, *, value: int | None = None
) -> Result[ArticleNumberSequence, None]:
    """Create an article number sequence."""
    db_sequence = DbArticleNumberSequence(shop_id, prefix, value=value)

    db.session.add(db_sequence)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return Err(None)

    sequence = _db_entity_to_article_number_sequence(db_sequence)

    return Ok(sequence)


def delete_article_number_sequence(
    sequence_id: ArticleNumberSequenceID,
) -> None:
    """Delete the article number sequence."""
    db.session.execute(
        delete(DbArticleNumberSequence).filter_by(id=sequence_id)
    )
    db.session.commit()


def get_article_number_sequence(
    sequence_id: ArticleNumberSequenceID,
) -> ArticleNumberSequence:
    """Return the article number sequence, or raise an exception."""
    db_sequence = db.session.execute(
        select(DbArticleNumberSequence).filter_by(id=sequence_id)
    ).scalar_one_or_none()

    if db_sequence is None:
        raise ValueError(f'Unknown article number sequence ID "{sequence_id}"')

    return _db_entity_to_article_number_sequence(db_sequence)


def get_article_number_sequences_for_shop(
    shop_id: ShopID,
) -> list[ArticleNumberSequence]:
    """Return the article number sequences defined for that shop."""
    db_sequences = db.session.scalars(
        select(DbArticleNumberSequence).filter_by(shop_id=shop_id)
    ).all()

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
    db_sequence = db.session.execute(
        select(DbArticleNumberSequence)
        .filter_by(id=sequence_id)
        .with_for_update()
    ).scalar_one_or_none()

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
        archived=db_sequence.archived,
    )
