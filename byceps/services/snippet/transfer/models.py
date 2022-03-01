"""
byceps.services.snippet.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import NewType
from uuid import UUID

from ...site.transfer.models import SiteID

from ....typing import BrandID


@dataclass(frozen=True)
class Scope:
    type_: str
    name: str

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


@dataclass(frozen=True)
class Mountpoint:
    id: MountpointID
    site_id: SiteID
    endpoint_suffix: str
    url_path: str
    snippet_id: SnippetID
