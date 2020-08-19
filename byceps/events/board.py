"""
byceps.events.board
~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from typing import Optional

from ..services.board.transfer.models import CategoryID, PostingID, TopicID
from ..typing import UserID

from .base import _BaseEvent


# topic


@dataclass(frozen=True)
class _BoardTopicEvent(_BaseEvent):
    topic_id: TopicID
    topic_title: str
    url: str


@dataclass(frozen=True)
class _BoardTopicModerationEvent(_BoardTopicEvent):
    moderator_id: UserID
    moderator_screen_name: Optional[str]


@dataclass(frozen=True)
class BoardTopicCreated(_BoardTopicEvent):
    pass


@dataclass(frozen=True)
class BoardTopicUpdated(_BoardTopicEvent):
    editor_id: UserID
    editor_screen_name: Optional[str]


@dataclass(frozen=True)
class BoardTopicHidden(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True)
class BoardTopicUnhidden(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True)
class BoardTopicLocked(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True)
class BoardTopicUnlocked(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True)
class BoardTopicPinned(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True)
class BoardTopicUnpinned(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True)
class BoardTopicMoved(_BoardTopicModerationEvent):
    old_category_id: CategoryID
    old_category_title: str
    new_category_id: CategoryID
    new_category_title: str


# posting


@dataclass(frozen=True)
class _BoardPostingEvent(_BaseEvent):
    posting_id: PostingID
    topic_title: str
    url: str


@dataclass(frozen=True)
class _BoardPostingModerationEvent(_BoardPostingEvent):
    moderator_id: UserID
    moderator_screen_name: Optional[str]


@dataclass(frozen=True)
class BoardPostingCreated(_BoardPostingEvent):
    topic_muted: bool


@dataclass(frozen=True)
class BoardPostingUpdated(_BoardPostingEvent):
    editor_id: UserID
    editor_screen_name: Optional[str]


@dataclass(frozen=True)
class BoardPostingHidden(_BoardPostingModerationEvent):
    pass


@dataclass(frozen=True)
class BoardPostingUnhidden(_BoardPostingModerationEvent):
    pass
