"""
byceps.services.newsletter.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import _BaseEvent, EventUser
from byceps.services.newsletter.models import ListID


@dataclass(frozen=True, kw_only=True)
class NewsletterEvent(_BaseEvent):
    user: EventUser
    list_id: ListID
    list_title: str


@dataclass(frozen=True, kw_only=True)
class SubscribedToNewsletterEvent(NewsletterEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UnsubscribedFromNewsletterEvent(NewsletterEvent):
    pass
