"""
byceps.services.news.models.channel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ....database import db
from ....typing import BrandID
from ....util.instances import ReprBuilder

from ..transfer.models import ChannelID


class Channel(db.Model):
    """A channel to which news items can be published."""
    __tablename__ = 'news_channels'

    id = db.Column(db.Unicode(40), primary_key=True)
    brand_id = db.Column(db.Unicode(20), db.ForeignKey('brands.id'), index=True, nullable=False)

    def __init__(self, channel_id: ChannelID, brand_id: BrandID) -> None:
        self.id = channel_id
        self.brand_id = brand_id

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add('brand', self.brand_id) \
            .build()
