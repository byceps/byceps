"""
byceps.services.news.dbmodels.image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Optional

from byceps.database import db
from byceps.services.news.models import NewsImageID, NewsItemID
from byceps.typing import UserID
from byceps.util.instances import ReprBuilder

from .item import DbNewsItem


class DbNewsImage(db.Model):
    """An image to illustrate a news item."""

    __tablename__ = 'news_images'
    __table_args__ = (
        db.UniqueConstraint('item_id', 'number'),
    )

    id = db.Column(db.Uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(
        db.Uuid, db.ForeignKey('news_items.id'), index=True, nullable=False
    )
    item = db.relationship(DbNewsItem, backref='images')
    number = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.UnicodeText, nullable=False)
    alt_text = db.Column(db.UnicodeText, nullable=True)
    caption = db.Column(db.UnicodeText, nullable=True)
    attribution = db.Column(db.UnicodeText, nullable=True)

    def __init__(
        self,
        image_id: NewsImageID,
        creator_id: UserID,
        item_id: NewsItemID,
        number: int,
        filename: str,
        *,
        alt_text: Optional[str] = None,
        caption: Optional[str] = None,
        attribution: Optional[str] = None,
    ) -> None:
        self.id = image_id
        self.creator_id = creator_id
        self.item_id = item_id
        self.number = number
        self.filename = filename
        self.alt_text = alt_text
        self.caption = caption
        self.attribution = attribution

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add_with_lookup('item_id')
            .add_with_lookup('number')
            .build()
        )
