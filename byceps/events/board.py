"""
byceps.events.board
~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass

from byceps.services.board.models import (
    BoardCategoryID,
    BoardID,
    PostingID,
    TopicID,
)
from byceps.typing import BrandID, UserID

from .base import _BaseEvent


@dataclass(frozen=True)
class _BoardEvent(_BaseEvent):
    brand_id: BrandID
    brand_title: str
    board_id: BoardID


# topic


@dataclass(frozen=True)
class _BoardTopicEvent(_BoardEvent):
    topic_id: TopicID
    topic_creator_id: UserID
    topic_creator_screen_name: str | None
    topic_title: str
    url: str


@dataclass(frozen=True)
class _BoardTopicModerationEvent(_BoardTopicEvent):
    moderator_id: UserID
    moderator_screen_name: str | None


@dataclass(frozen=True)
class BoardTopicCreatedEvent(_BoardTopicEvent):
    pass


@dataclass(frozen=True)
class BoardTopicUpdatedEvent(_BoardTopicEvent):
    editor_id: UserID
    editor_screen_name: str | None


@dataclass(frozen=True)
class BoardTopicHiddenEvent(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True)
class BoardTopicUnhiddenEvent(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True)
class BoardTopicLockedEvent(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True)
class BoardTopicUnlockedEvent(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True)
class BoardTopicPinnedEvent(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True)
class BoardTopicUnpinnedEvent(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True)
class BoardTopicMovedEvent(_BoardTopicModerationEvent):
    old_category_id: BoardCategoryID
    old_category_title: str
    new_category_id: BoardCategoryID
    new_category_title: str


# posting


@dataclass(frozen=True)
class _BoardPostingEvent(_BoardEvent):
    posting_id: PostingID
    posting_creator_id: UserID
    posting_creator_screen_name: str | None
    topic_id: TopicID
    topic_title: str
    url: str


@dataclass(frozen=True)
class _BoardPostingModerationEvent(_BoardPostingEvent):
    moderator_id: UserID
    moderator_screen_name: str | None


@dataclass(frozen=True)
class BoardPostingCreatedEvent(_BoardPostingEvent):
    topic_muted: bool


@dataclass(frozen=True)
class BoardPostingUpdatedEvent(_BoardPostingEvent):
    editor_id: UserID
    editor_screen_name: str | None


@dataclass(frozen=True)
class BoardPostingHiddenEvent(_BoardPostingModerationEvent):
    pass


@dataclass(frozen=True)
class BoardPostingUnhiddenEvent(_BoardPostingModerationEvent):
    pass
