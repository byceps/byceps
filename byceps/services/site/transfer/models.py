"""
byceps.services.site.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType

from attr import attrib, attrs


from ....typing import PartyID


SiteID = NewType('SiteID', str)


@attrs(frozen=True, slots=True)
class Site:
    id = attrib(type=SiteID)
    party_id = attrib(type=PartyID)
    title = attrib(type=str)


@attrs(frozen=True, slots=True)
class SiteSetting:
    site_id = attrib(type=SiteID)
    name = attrib(type=str)
    value = attrib(type=str)
