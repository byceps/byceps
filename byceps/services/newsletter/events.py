"""
byceps.services.newsletter.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.core.events import BaseEvent
from byceps.services.newsletter.models import ListID
from byceps.services.user.models import User


@dataclass(frozen=True, kw_only=True)
class NewsletterEvent(BaseEvent):
    user: User
    list_id: ListID
    list_title: str


@dataclass(frozen=True, kw_only=True)
class SubscribedToNewsletterEvent(NewsletterEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class UnsubscribedFromNewsletterEvent(NewsletterEvent):
    pass
