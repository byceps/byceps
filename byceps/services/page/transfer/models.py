"""
byceps.services.page.transfer.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import NewType, Optional
from uuid import UUID

from ....typing import UserID

from ...site.transfer.models import SiteID


PageID = NewType('PageID', UUID)


VersionID = NewType('VersionID', UUID)


@dataclass(frozen=True)
class Page:
    id: PageID
    site_id: SiteID
    name: str
    language_code: str
    url_path: str
    published: bool


@dataclass(frozen=True)
class Version:
    id: VersionID
    page_id: PageID
    created_at: datetime
    creator_id: UserID
    title: str
    head: Optional[str]
    body: str


@dataclass(frozen=True)
class PageAggregate(Page):
    title: str
    head: Optional[str]
    body: str
