"""
byceps.services.site.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType

from byceps.services.board.models import BoardID
from byceps.services.brand.models import Brand, BrandID
from byceps.services.news.models import NewsChannelID
from byceps.services.party.models import PartyID
from byceps.services.shop.storefront.models import StorefrontID


SiteID = NewType('SiteID', str)


@dataclass(frozen=True, kw_only=True)
class Site:
    id: SiteID
    title: str
    server_name: str
    brand_id: BrandID
    party_id: PartyID | None
    enabled: bool
    user_account_creation_enabled: bool
    login_enabled: bool
    news_channel_ids: set[NewsChannelID]
    board_id: BoardID | None
    storefront_id: StorefrontID | None
    is_intranet: bool
    check_in_on_login: bool
    archived: bool


@dataclass(frozen=True, kw_only=True)
class SiteWithBrand(Site):
    brand: Brand


@dataclass(frozen=True, kw_only=True)
class SiteSetting:
    site_id: SiteID
    name: str
    value: str
