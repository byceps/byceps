"""
byceps.services.shop.article.dbmodels.sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from .....database import db, generate_uuid
from .....util.instances import ReprBuilder

from ...shop.transfer.models import ShopID


class DbArticleNumberSequence(db.Model):
    """A shop-specific, unique article number sequence."""

    __tablename__ = 'shop_article_number_sequences'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    shop_id = db.Column(
        db.UnicodeText, db.ForeignKey('shops.id'), index=True, nullable=False
    )
    prefix = db.Column(db.UnicodeText, unique=True, nullable=False)
    value = db.Column(db.Integer, default=0, nullable=False)

    def __init__(
        self,
        shop_id: ShopID,
        prefix: str,
        *,
        value: Optional[int] = 0,
    ) -> None:
        if value is None:
            value = 0

        self.shop_id = shop_id
        self.prefix = prefix
        self.value = value

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('shop', self.shop_id) \
            .add_with_lookup('prefix') \
            .add_with_lookup('value') \
            .build()
