"""
byceps.services.news.dbmodels.channel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from byceps.database import db
from byceps.services.news.models import NewsChannelID
from byceps.services.site.models import SiteID
from byceps.typing import BrandID
from byceps.util.instances import ReprBuilder


class DbNewsChannel(db.Model):
    """A channel to which news items can be published."""

    __tablename__ = 'news_channels'

    id: Mapped[NewsChannelID] = mapped_column(db.UnicodeText, primary_key=True)
    brand_id: Mapped[BrandID] = mapped_column(
        db.UnicodeText, db.ForeignKey('brands.id'), index=True
    )
    announcement_site_id: Mapped[SiteID | None] = mapped_column(
        db.UnicodeText, db.ForeignKey('sites.id')
    )
    archived: Mapped[bool] = mapped_column(default=False)

    def __init__(
        self,
        channel_id: NewsChannelID,
        brand_id: BrandID,
        *,
        announcement_site_id: SiteID | None = None,
    ) -> None:
        self.id = channel_id
        self.brand_id = brand_id
        self.announcement_site_id = announcement_site_id

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add('brand', self.brand_id)
            .build()
        )
