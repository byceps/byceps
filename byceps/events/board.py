"""
byceps.events.board
~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from typing import Optional

from byceps.services.board.models import (
    BoardCategoryID,
    BoardID,
    PostingID,
    TopicID,
)
from byceps.typing import UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class _BoardEvent(_BaseEvent):
    board_id: BoardID


# topic


@dataclass(frozen=True)
class _BoardTopicEvent(_BoardEvent):
    topic_id: TopicID
    topic_creator_id: UserID
    topic_creator_screen_name: Optional[str]
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
    old_category_id: BoardCategoryID
    old_category_title: str
    new_category_id: BoardCategoryID
    new_category_title: str


# posting


@dataclass(frozen=True)
class _BoardPostingEvent(_BoardEvent):
    posting_id: PostingID
    posting_creator_id: UserID
    posting_creator_screen_name: Optional[str]
    topic_id: TopicID
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
