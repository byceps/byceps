"""
byceps.services.snippet.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from ...typing import BrandID

from ..site.models import SiteID


@dataclass(frozen=True)
class SnippetScope:
    type_: str
    name: str

    @classmethod
    def for_brand(cls, brand_id: BrandID) -> SnippetScope:
        return cls('brand', str(brand_id))

    @classmethod
    def for_site(cls, site_id: SiteID) -> SnippetScope:
        return cls('site', str(site_id))


SnippetID = NewType('SnippetID', UUID)


SnippetVersionID = NewType('SnippetVersionID', UUID)
