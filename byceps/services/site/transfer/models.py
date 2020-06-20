"""
byceps.services.site.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import NewType, Optional

from ....typing import BrandID, PartyID

from ...board.transfer.models import BoardID
from ...news.transfer.models import ChannelID as NewsChannelID
from ...shop.storefront.transfer.models import StorefrontID


SiteID = NewType('SiteID', str)


@dataclass(frozen=True)
class Site:
    id: SiteID
    title: str
    server_name: str
    brand_id: BrandID
    email_config_id: str
    party_id: PartyID
    enabled: bool
    user_account_creation_enabled: bool
    login_enabled: bool
    news_channel_id: Optional[NewsChannelID]
    board_id: Optional[BoardID]
    storefront_id: Optional[StorefrontID]
    archived: bool


@dataclass(frozen=True)
class SiteSetting:
    site_id: SiteID
    name: str
    value: str
