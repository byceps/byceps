"""
byceps.events.newsletter
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.events.base import EventUser
from byceps.services.newsletter.models import ListID

from .base import _BaseEvent


@dataclass(frozen=True)
class NewsletterEvent(_BaseEvent):
    user: EventUser
    list_id: ListID
    list_title: str


@dataclass(frozen=True)
class SubscribedToNewsletterEvent(NewsletterEvent):
    pass


@dataclass(frozen=True)
class UnsubscribedFromNewsletterEvent(NewsletterEvent):
    pass
