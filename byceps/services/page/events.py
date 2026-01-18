"""
byceps.services.page.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import BaseEvent, EventSite
from byceps.services.page.models import PageID, PageVersionID


@dataclass(frozen=True, kw_only=True)
class _PageEvent(BaseEvent):
    page_id: PageID
    site: EventSite
    page_name: str
    language_code: str


@dataclass(frozen=True, kw_only=True)
class PageCreatedEvent(_PageEvent):
    page_version_id: PageVersionID


@dataclass(frozen=True, kw_only=True)
class PageUpdatedEvent(_PageEvent):
    page_version_id: PageVersionID


@dataclass(frozen=True, kw_only=True)
class PageDeletedEvent(_PageEvent):
    pass
