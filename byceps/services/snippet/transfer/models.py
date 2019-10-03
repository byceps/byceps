"""
byceps.services.snippet.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from __future__ import annotations
from enum import Enum
from typing import NewType
from uuid import UUID

from attr import attrs

from ...site.transfer.models import SiteID

from ....typing import BrandID


@attrs(auto_attribs=True, frozen=True, slots=True)
class Scope:
    type_: str
    name: str

    @classmethod
    def for_global(cls) -> Scope:
        return cls('global', 'global')

    @classmethod
    def for_brand(cls, brand_id: BrandID) -> Scope:
        return cls('brand', str(brand_id))

    @classmethod
    def for_site(cls, site_id: SiteID) -> Scope:
        return cls('site', str(site_id))


SnippetID = NewType('SnippetID', UUID)


SnippetType = Enum('SnippetType', ['document', 'fragment'])


SnippetVersionID = NewType('SnippetVersionID', UUID)


MountpointID = NewType('MountpointID', UUID)
