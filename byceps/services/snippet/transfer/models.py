"""
byceps.services.snippet.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from enum import Enum
from typing import NewType
from uuid import UUID

from attr import attrib, attrs

from ...site.transfer.models import SiteID


@attrs(frozen=True, slots=True)
class Scope:
    type_ = attrib(type=str)
    name = attrib(type=str)

    @classmethod
    def for_site(cls, site_id: SiteID):
        return cls('site', str(site_id))


SnippetID = NewType('SnippetID', UUID)


SnippetType = Enum('SnippetType', ['document', 'fragment'])


SnippetVersionID = NewType('SnippetVersionID', UUID)


MountpointID = NewType('MountpointID', UUID)
