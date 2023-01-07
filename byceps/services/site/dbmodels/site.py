"""
byceps.services.site.dbmodels.site
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ....database import db
from ....typing import BrandID, PartyID
from ....util.instances import ReprBuilder

from ...board.transfer.models import BoardID
from ...brand.dbmodels.brand import DbBrand
from ...news.dbmodels.channel import DbNewsChannel
from ...shop.storefront.transfer.models import StorefrontID

from ..transfer.models import SiteID


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
        party_id: Optional[PartyID] = None,
        board_id: Optional[BoardID] = None,
        storefront_id: Optional[StorefrontID] = None,
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

    def __repr__(self) -> str:
        return ReprBuilder(self).add_with_lookup('id').build()
