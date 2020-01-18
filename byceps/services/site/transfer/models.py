"""
byceps.services.site.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType

from attr import attrs

from ....typing import PartyID


SiteID = NewType('SiteID', str)


@attrs(auto_attribs=True, frozen=True, slots=True)
class Site:
    id: SiteID
    title: str
    server_name: str
    email_config_id: str
    party_id: PartyID
    enabled: bool
    user_account_creation_enabled: bool
    login_enabled: bool
    archived: bool


@attrs(auto_attribs=True, frozen=True, slots=True)
class SiteSetting:
    site_id: SiteID
    name: str
    value: str
