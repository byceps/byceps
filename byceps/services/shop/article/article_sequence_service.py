"""
byceps.services.shop.article.article_sequence_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy import delete, select, update
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


def generate_article_number(
    sequence_id: ArticleNumberSequenceID,
) -> Result[ArticleNumber, str]:
    """Generate and reserve the next article number from this sequence."""
    row = db.session.execute(
        update(DbArticleNumberSequence)
        .filter_by(id=sequence_id)
        .values(value=DbArticleNumberSequence.value + 1)
        .returning(
            DbArticleNumberSequence.prefix, DbArticleNumberSequence.value
        )
    ).one_or_none()
    db.session.commit()

    if row is None:
        return Err(f'No article number sequence found for ID "{sequence_id}".')

    prefix, value = row
    article_number = ArticleNumber(f'{prefix}{value:05d}')

    return Ok(article_number)


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
