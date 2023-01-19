"""
byceps.services.page.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import NewType, Optional
from uuid import UUID

from ...typing import UserID

from ..site.models import SiteID
from ..site_navigation.models import NavMenuID


PageID = NewType('PageID', UUID)


PageVersionID = NewType('PageVersionID', UUID)


@dataclass(frozen=True)
class Page:
    id: PageID
    site_id: SiteID
    name: str
    language_code: str
    url_path: str
    published: bool
    nav_menu_id: NavMenuID


@dataclass(frozen=True)
class PageVersion:
    id: PageVersionID
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
