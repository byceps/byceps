"""
byceps.services.site.models.site
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from ....database import db
from ....typing import BrandID, PartyID
from ....util.instances import ReprBuilder

from ...board.transfer.models import BoardID
from ...news.transfer.models import ChannelID as NewsChannelID
from ...shop.storefront.transfer.models import StorefrontID

from ..transfer.models import SiteID


class Site(db.Model):
    """A site."""

    __tablename__ = 'sites'

    id = db.Column(db.UnicodeText, primary_key=True)
    title = db.Column(db.UnicodeText, unique=True, nullable=False)
    server_name = db.Column(db.UnicodeText, unique=True, nullable=False)
    brand_id = db.Column(db.UnicodeText, db.ForeignKey('brands.id'), index=True, nullable=False)
    email_config_id = db.Column(db.UnicodeText, db.ForeignKey('email_configs.id'), nullable=False)
    party_id = db.Column(db.UnicodeText, db.ForeignKey('parties.id'), index=True, nullable=True)
    enabled = db.Column(db.Boolean, nullable=False)
    user_account_creation_enabled = db.Column(db.Boolean, nullable=False)
    login_enabled = db.Column(db.Boolean, nullable=False)
    news_channel_id = db.Column(db.UnicodeText, db.ForeignKey('news_channels.id'), index=True, nullable=True)
    board_id = db.Column(db.UnicodeText, db.ForeignKey('boards.id'), index=True, nullable=True)
    storefront_id = db.Column(db.UnicodeText, db.ForeignKey('shop_storefronts.id'), index=True, nullable=True)
    archived = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(
        self,
        site_id: SiteID,
        title: str,
        server_name: str,
        brand_id: BrandID,
        email_config_id: str,
        enabled: bool,
        user_account_creation_enabled: bool,
        login_enabled: bool,
        *,
        party_id: Optional[PartyID] = None,
        news_channel_id: Optional[NewsChannelID] = None,
        board_id: Optional[BoardID] = None,
        storefront_id: Optional[StorefrontID] = None,
    ) -> None:
        self.id = site_id
        self.title = title
        self.server_name = server_name
        self.brand_id = brand_id
        self.email_config_id = email_config_id
        self.party_id = party_id
        self.enabled = enabled
        self.user_account_creation_enabled = user_account_creation_enabled
        self.login_enabled = login_enabled
        self.news_channel_id = news_channel_id
        self.board_id = board_id
        self.storefront_id = storefront_id

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()
