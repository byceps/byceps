"""
byceps.events.page
~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.page.models import PageID, PageVersionID

from .base import _BaseEvent, EventSite


@dataclass(frozen=True)
class _PageEvent(_BaseEvent):
    page_id: PageID
    site: EventSite
    page_name: str
    language_code: str


@dataclass(frozen=True)
class PageCreatedEvent(_PageEvent):
    page_version_id: PageVersionID


@dataclass(frozen=True)
class PageUpdatedEvent(_PageEvent):
    page_version_id: PageVersionID


@dataclass(frozen=True)
class PageDeletedEvent(_PageEvent):
    pass
