"""
byceps.services.newsletter.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import NewType

from byceps.services.user.models import UserID


ListID = NewType('ListID', str)


@dataclass(frozen=True, kw_only=True)
class List:
    id: ListID
    title: str


@dataclass(frozen=True, kw_only=True)
class Subscriber:
    screen_name: str
    email_address: str


SubscriptionState = Enum('SubscriptionState', ['requested', 'declined'])


@dataclass(frozen=True, kw_only=True)
class SubscriptionUpdate:
    user_id: UserID
    list_id: ListID
    expressed_at: datetime
    state: SubscriptionState
