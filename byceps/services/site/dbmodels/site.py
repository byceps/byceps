"""
byceps.services.site.dbmodels.site
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from byceps.database import db
from byceps.services.board.models import BoardID
from byceps.services.brand.dbmodels.brand import DbBrand
from byceps.services.news.dbmodels.channel import DbNewsChannel
from byceps.services.shop.storefront.models import StorefrontID
from byceps.services.site.models import SiteID
from byceps.typing import BrandID, PartyID
from byceps.util.instances import ReprBuilder


site_news_channels = db.Table(
    'site_news_channels',
    db.Column(
        'site_id', db.UnicodeText, db.ForeignKey('sites.id'), primary_key=True
    ),
    db.Column(
        'news_channel_id',
        db.UnicodeText,
        db.ForeignKey('news_channels.id'),
        primary_key=True,
    ),
)


class DbSite(db.Model):
    """A site."""

    __tablename__ = 'sites'

    id = db.Column(db.UnicodeText, primary_key=True)
    title = db.Column(db.UnicodeText, unique=True, nullable=False)
    server_name = db.Column(db.UnicodeText, unique=True, nullable=False)
    brand_id = db.Column(
        db.UnicodeText, db.ForeignKey('brands.id'), index=True, nullable=False
    )
    brand = db.relationship(DbBrand, backref='sites')
    party_id = db.Column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True, nullable=True
    )
    enabled = db.Column(db.Boolean, nullable=False)
    user_account_creation_enabled = db.Column(db.Boolean, nullable=False)
    login_enabled = db.Column(db.Boolean, nullable=False)
    board_id = db.Column(
        db.UnicodeText, db.ForeignKey('boards.id'), index=True, nullable=True
    )
    storefront_id = db.Column(
        db.UnicodeText,
        db.ForeignKey('shop_storefronts.id'),
        index=True,
        nullable=True,
    )
    is_intranet = db.Column(db.Boolean, nullable=False)
    archived = db.Column(db.Boolean, default=False, nullable=False)

    news_channels = db.relationship(
        DbNewsChannel,
        secondary=site_news_channels,
        lazy='subquery',
        backref=db.backref('news_channels', lazy=True),
    )

    def __init__(
        self,
        site_id: SiteID,
        title: str,
        server_name: str,
        brand_id: BrandID,
        enabled: bool,
        user_account_creation_enabled: bool,
        login_enabled: bool,
        *,
        party_id: PartyID | None = None,
        board_id: BoardID | None = None,
        storefront_id: StorefrontID | None = None,
        is_intranet: bool = False,
    ) -> None:
        self.id = site_id
        self.title = title
        self.server_name = server_name
        self.brand_id = brand_id
        self.party_id = party_id
        self.enabled = enabled
        self.user_account_creation_enabled = user_account_creation_enabled
        self.login_enabled = login_enabled
        self.board_id = board_id
        self.storefront_id = storefront_id
        self.is_intranet = is_intranet

    def __repr__(self) -> str:
        return ReprBuilder(self).add_with_lookup('id').build()
