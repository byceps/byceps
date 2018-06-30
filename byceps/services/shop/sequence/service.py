"""
byceps.services.shop.sequence.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ....database import db

from ..article.transfer.models import ArticleNumber
from ..order.transfer.models import OrderNumber

from ..shop.transfer.models import ShopID

from .models import NumberSequence
from .transfer.models import Purpose


def create_sequence(shop_id: ShopID, purpose: Purpose, prefix: str) -> None:
    """Create a sequence for that shop and purpose."""
    sequence = NumberSequence(shop_id, purpose, prefix)

    db.session.add(sequence)
    db.session.commit()


class NumberGenerationFailed(Exception):
    """Indicate that generating a prefixed, sequential number has failed."""

    def __init__(self, message: str) -> None:
        self.message = message


def generate_article_number(shop_id: ShopID) -> ArticleNumber:
    """Generate and reserve an unused, unique article number for this shop."""
    prefix = get_article_number_prefix(shop_id)

    if prefix is None:
        raise NumberGenerationFailed(
            'No article number prefix is configured for shop "{}".'
            .format(shop_id))

    article_sequence_number = _get_next_sequence_number(shop_id,
        Purpose.article)

    return ArticleNumber('{}{:05d}'.format(prefix, article_sequence_number))


def generate_order_number(shop_id: ShopID) -> OrderNumber:
    """Generate and reserve an unused, unique order number for this shop."""
    prefix = get_order_number_prefix(shop_id)

    if prefix is None:
        raise NumberGenerationFailed(
            'No order number prefix is configured for shop "{}".'
            .format(shop_id))

    order_sequence_number = _get_next_sequence_number(shop_id, Purpose.order)

    return OrderNumber('{}{:05d}'.format(prefix, order_sequence_number))


def _get_next_sequence_number(shop_id: ShopID, purpose: Purpose) -> int:
    """Calculate and reserve the next sequence number for the shop and
    purpose.
    """
    sequence = NumberSequence.query \
        .filter_by(shop_id=shop_id) \
        .filter_by(_purpose=purpose.name) \
        .with_for_update() \
        .one_or_none()

    if sequence is None:
        raise NumberGenerationFailed(
            'No sequence configured for shop "{}" and purpose "{}".'
            .format(shop_id, purpose.name))

    sequence.value = NumberSequence.value + 1
    db.session.commit()
    return sequence.value


def get_article_number_prefix(shop_id: ShopID) -> Optional[str]:
    """Return the article number prefix for that shop, or `None` if
    none is defined.
    """
    return _find_prefix_attr(shop_id, Purpose.article)


def get_order_number_prefix(shop_id: ShopID) -> Optional[str]:
    """Return the order number prefix for that shop, or `None` if
    none is defined.
    """
    return _find_prefix_attr(shop_id, Purpose.order)


def _find_prefix_attr(shop_id: ShopID, purpose: Purpose) -> Optional[str]:
    sequence = NumberSequence.query.get((shop_id, purpose.name))
    return getattr(sequence, 'prefix', None)
