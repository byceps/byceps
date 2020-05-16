"""
byceps.services.site.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import NewType

from ....typing import PartyID

from ...shop.storefront.transfer.models import StorefrontID


SiteID = NewType('SiteID', str)


@dataclass(frozen=True)
class Site:
    id: SiteID
    title: str
    server_name: str
    email_config_id: str
    party_id: PartyID
    enabled: bool
    user_account_creation_enabled: bool
    login_enabled: bool
    storefront_id: StorefrontID
    archived: bool


@dataclass(frozen=True)
class SiteSetting:
    site_id: SiteID
    name: str
    value: str
