"""
byceps.events.page
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.page.models import PageID, PageVersionID
from byceps.services.site.models import SiteID

from .base import _BaseEvent


@dataclass(frozen=True)
class _PageEvent(_BaseEvent):
    page_id: PageID
    site_id: SiteID
    page_name: str


@dataclass(frozen=True)
class PageCreated(_PageEvent):
    page_version_id: PageVersionID


@dataclass(frozen=True)
class PageUpdated(_PageEvent):
    page_version_id: PageVersionID


@dataclass(frozen=True)
class PageDeleted(_PageEvent):
    pass
