"""
byceps.events.page
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from ..services.page.transfer.models import PageID, VersionID
from ..services.site.transfer.models import SiteID

from .base import _BaseEvent


@dataclass(frozen=True)
class _PageEvent(_BaseEvent):
    page_id: PageID
    site_id: SiteID
    page_name: str


@dataclass(frozen=True)
class PageCreated(_PageEvent):
    page_version_id: VersionID


@dataclass(frozen=True)
class PageUpdated(_PageEvent):
    page_version_id: VersionID


@dataclass(frozen=True)
class PageDeleted(_PageEvent):
    pass
