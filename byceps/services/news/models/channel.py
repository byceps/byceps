"""
byceps.services.news.models.channel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ....database import db
from ....typing import BrandID
from ....util.instances import ReprBuilder

from ..transfer.models import ChannelID


class Channel(db.Model):
    """A channel to which news items can be published."""

    __tablename__ = 'news_channels'

    id = db.Column(db.UnicodeText, primary_key=True)
    brand_id = db.Column(db.UnicodeText, db.ForeignKey('brands.id'), index=True, nullable=False)
    url_prefix = db.Column(db.UnicodeText, nullable=False)

    def __init__(
        self, channel_id: ChannelID, brand_id: BrandID, url_prefix: str
    ) -> None:
        self.id = channel_id
        self.brand_id = brand_id
        self.url_prefix = url_prefix

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('brand', self.brand_id) \
            .build()
