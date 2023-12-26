"""
byceps.services.shop.article.dbmodels.sequence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.shop.article.models import ArticleNumberSequenceID
from byceps.services.shop.shop.models import ShopID
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid4


class DbArticleNumberSequence(db.Model):
    """A shop-specific, unique article number sequence."""

    __tablename__ = 'shop_article_number_sequences'

    id: Mapped[ArticleNumberSequenceID] = mapped_column(
        db.Uuid, default=generate_uuid4, primary_key=True
    )
    shop_id: Mapped[ShopID] = mapped_column(
        db.UnicodeText, db.ForeignKey('shops.id'), index=True
    )
    prefix: Mapped[str] = mapped_column(db.UnicodeText, unique=True)
    value: Mapped[int] = mapped_column(default=0)
    archived: Mapped[bool] = mapped_column(default=False)

    def __init__(
        self,
        shop_id: ShopID,
        prefix: str,
        *,
        value: int | None = 0,
    ) -> None:
        if value is None:
            value = 0

        self.shop_id = shop_id
        self.prefix = prefix
        self.value = value

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add('shop', self.shop_id)
            .add_with_lookup('prefix')
            .add_with_lookup('value')
            .build()
        )
