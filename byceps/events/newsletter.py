"""
byceps.events.newsletter
~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.services.newsletter.models import ListID
from byceps.services.user.models.user import UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class NewsletterEvent(_BaseEvent):
    user_id: UserID
    user_screen_name: str | None
    list_id: ListID
    list_title: str


@dataclass(frozen=True)
class SubscribedToNewsletterEvent(NewsletterEvent):
    pass


@dataclass(frozen=True)
class UnsubscribedFromNewsletterEvent(NewsletterEvent):
    pass
