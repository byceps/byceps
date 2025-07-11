"""
byceps.services.page.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import NewType
from uuid import UUID

from byceps.services.site.models import SiteID
from byceps.services.site_navigation.models import NavMenuID
from byceps.services.user.models.user import UserID


PageID = NewType('PageID', UUID)


PageVersionID = NewType('PageVersionID', UUID)


@dataclass(frozen=True, kw_only=True)
class Page:
    id: PageID
    site_id: SiteID
    name: str
    language_code: str
    url_path: str
    published: bool
    nav_menu_id: NavMenuID | None

    @property
    def current_page_id(self) -> str:
        return 'page_' + self.name


@dataclass(frozen=True, kw_only=True)
class PageVersion:
    id: PageVersionID
    page_id: PageID
    created_at: datetime
    creator_id: UserID
    title: str
    head: str | None
    body: str


@dataclass(frozen=True, kw_only=True)
class PageAggregate(Page):
    title: str
    head: str | None
    body: str
