"""
byceps.services.shop.sequence.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ....database import db

from ..article.transfer.models import ArticleNumber
from ..order.transfer.models import OrderNumber

from ..shop.transfer.models import ShopID

from .models import NumberSequence as DbNumberSequence
from .transfer.models import NumberSequence, Purpose


def create_sequence(shop_id: ShopID, purpose: Purpose, prefix: str) -> None:
    """Create a sequence for that shop and purpose."""
    sequence = DbNumberSequence(shop_id, purpose, prefix)

    db.session.add(sequence)
    db.session.commit()


class NumberGenerationFailed(Exception):
    """Indicate that generating a prefixed, sequential number has failed."""

    def __init__(self, message: str) -> None:
        self.message = message


def generate_article_number(shop_id: ShopID) -> ArticleNumber:
    """Generate and reserve an unused, unique article number for this shop."""
    sequence = _get_next_sequence_step(shop_id, Purpose.article)

    return format_article_number(sequence)


def generate_order_number(shop_id: ShopID) -> OrderNumber:
    """Generate and reserve an unused, unique order number for this shop."""
    sequence = _get_next_sequence_step(shop_id, Purpose.order)

    return format_order_number(sequence)


def _get_next_sequence_step(
    shop_id: ShopID, purpose: Purpose
) -> NumberSequence:
    """Calculate and reserve the next sequence step for the shop and
    purpose.
    """
    sequence = DbNumberSequence.query \
        .filter_by(shop_id=shop_id) \
        .filter_by(_purpose=purpose.name) \
        .with_for_update() \
        .one_or_none()

    if sequence is None:
        raise NumberGenerationFailed(
            f'No sequence configured for shop "{shop_id}" '
            f'and purpose "{purpose.name}".'
        )

    sequence.value = DbNumberSequence.value + 1
    db.session.commit()

    return sequence


def format_article_number(sequence: NumberSequence) -> ArticleNumber:
    """Format a number sequence step as article number."""
    return ArticleNumber(f'{sequence.prefix}{sequence.value:05d}')


def format_order_number(sequence: NumberSequence) -> OrderNumber:
    """Format a number sequence step as order number."""
    return OrderNumber(f'{sequence.prefix}{sequence.value:05d}')


def find_article_number_sequence(shop_id: ShopID) -> Optional[NumberSequence]:
    """Return the article number sequence for that shop, or `None` if
    the sequence is not defined or the shop does not exist.
    """
    return _find_number_sequence(shop_id, Purpose.article)


def find_order_number_sequence(shop_id: ShopID) -> Optional[NumberSequence]:
    """Return the order number sequence for that shop, or `None` if
    the sequence is not defined or the shop does not exist.
    """
    return _find_number_sequence(shop_id, Purpose.order)


def _find_number_sequence(
    shop_id: ShopID, purpose: Purpose
) -> Optional[NumberSequence]:
    sequence = DbNumberSequence.query.get((shop_id, purpose.name))

    if sequence is None:
        return None

    return _db_entity_to_number_sequence(sequence)


def _db_entity_to_number_sequence(entity: DbNumberSequence) -> NumberSequence:
    return NumberSequence(
        entity.shop_id,
        entity.purpose,
        entity.prefix,
        entity.value,
    )
