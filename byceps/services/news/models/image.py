"""
byceps.services.news.models.image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime
from typing import Optional

from ....database import db, generate_uuid
from ....typing import UserID
from ....util.instances import ReprBuilder

from ..transfer.models import ItemID

from .item import Item


class Image(db.Model):
    """An image to illustrate a news item."""

    __tablename__ = 'news_images'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Uuid, db.ForeignKey('news_items.id'), index=True, nullable=False)
    item = db.relationship(Item, backref='images')
    filename = db.Column(db.UnicodeText, nullable=False)
    alt_text = db.Column(db.UnicodeText, nullable=True)
    caption = db.Column(db.UnicodeText, nullable=True)

    def __init__(
        self,
        creator_id: UserID,
        item_id: ItemID,
        filename: str,
        *,
        alt_text: Optional[str] = None,
        caption: Optional[str] = None,
    ) -> None:
        self.creator_id = creator_id
        self.item_id = item_id
        self.filename = filename
        self.alt_text = alt_text
        self.caption = caption

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('item_id') \
            .add_with_lookup('filename') \
            .build()
