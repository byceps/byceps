"""
byceps.services.site.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType

from attr import attrib, attrs


SiteID = NewType('SiteID', str)


@attrs(frozen=True, slots=True)
class SiteSetting:
    site_id = attrib(type=SiteID)
    name = attrib(type=str)
    value = attrib(type=str)
