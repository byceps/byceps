"""
byceps.services.snippet.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import NewType
from uuid import UUID

from typing_extensions import Self

from byceps.services.site.models import SiteID
from byceps.typing import BrandID


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


SnippetID = NewType('SnippetID', UUID)


SnippetVersionID = NewType('SnippetVersionID', UUID)
