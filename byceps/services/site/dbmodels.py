"""
byceps.services.site.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.board.models import BoardID
from byceps.services.brand.dbmodels import DbBrand
from byceps.services.brand.models import BrandID
from byceps.services.news.dbmodels import DbNewsChannel
from byceps.services.party.models import PartyID
from byceps.services.shop.storefront.models import StorefrontID
from byceps.services.site.models import SiteID
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

    id: Mapped[SiteID] = mapped_column(db.UnicodeText, primary_key=True)
    title: Mapped[str] = mapped_column(db.UnicodeText, unique=True)
    server_name: Mapped[str] = mapped_column(db.UnicodeText, unique=True)
    brand_id: Mapped[BrandID] = mapped_column(
        db.UnicodeText, db.ForeignKey('brands.id'), index=True
    )
    brand: Mapped[DbBrand] = relationship(DbBrand, backref='sites')
    party_id: Mapped[PartyID | None] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True
    )
    enabled: Mapped[bool]
    user_account_creation_enabled: Mapped[bool]
    login_enabled: Mapped[bool]
    board_id: Mapped[BoardID | None] = mapped_column(
        db.UnicodeText, db.ForeignKey('boards.id'), index=True
    )
    storefront_id: Mapped[StorefrontID | None] = mapped_column(
        db.UnicodeText,
        db.ForeignKey('shop_storefronts.id'),
        index=True,
    )
    is_intranet: Mapped[bool]
    check_in_on_login: Mapped[bool]
    archived: Mapped[bool] = mapped_column(default=False)

    news_channels: Mapped[list[DbNewsChannel]] = relationship(
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
        check_in_on_login: bool = False,
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
        self.check_in_on_login = check_in_on_login

    def __repr__(self) -> str:
        return ReprBuilder(self).add_with_lookup('id').build()


class DbSiteSetting(db.Model):
    """A site-specific setting."""

    __tablename__ = 'site_settings'

    site_id: Mapped[SiteID] = mapped_column(
        db.UnicodeText, db.ForeignKey('sites.id'), primary_key=True, index=True
    )
    name: Mapped[str] = mapped_column(db.UnicodeText, primary_key=True)
    value: Mapped[str] = mapped_column(db.UnicodeText)

    def __init__(self, site_id: SiteID, name: str, value: str) -> None:
        self.site_id = site_id
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('site_id')
            .add_with_lookup('name')
            .add_with_lookup('value')
            .build()
        )
