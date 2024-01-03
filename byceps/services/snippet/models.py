"""
byceps.services.snippet.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType, Self
from uuid import UUID

from byceps.services.brand.models import BrandID
from byceps.services.site.models import SiteID


@dataclass(frozen=True)
class SnippetScope:
    type_: str
    name: str

    @classmethod
    def for_brand(cls, brand_id: BrandID) -> Self:
        return cls('brand', str(brand_id))

    @classmethod
    def for_site(cls, site_id: SiteID) -> Self:
        return cls('site', str(site_id))

    def as_string(self) -> str:
        return f'{self.type_}/{self.name}'


SnippetID = NewType('SnippetID', UUID)


SnippetVersionID = NewType('SnippetVersionID', UUID)
