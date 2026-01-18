"""
byceps.services.board.events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from byceps.services.board.models import (
    BoardCategoryID,
    BoardID,
    PostingID,
    TopicID,
)
from byceps.services.core.events import BaseEvent, EventBrand
from byceps.services.user.models.user import User


@dataclass(frozen=True, kw_only=True)
class _BoardEvent(BaseEvent):
    brand: EventBrand
    board_id: BoardID


# topic


@dataclass(frozen=True, kw_only=True)
class _BoardTopicEvent(_BoardEvent):
    topic_id: TopicID
    topic_creator: User
    topic_title: str
    url: str


@dataclass(frozen=True, kw_only=True)
class _BoardTopicModerationEvent(_BoardTopicEvent):
    moderator: User


@dataclass(frozen=True, kw_only=True)
class BoardTopicCreatedEvent(_BoardTopicEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class BoardTopicUpdatedEvent(_BoardTopicEvent):
    editor: User


@dataclass(frozen=True, kw_only=True)
class BoardTopicHiddenEvent(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class BoardTopicUnhiddenEvent(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class BoardTopicLockedEvent(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class BoardTopicUnlockedEvent(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class BoardTopicPinnedEvent(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class BoardTopicUnpinnedEvent(_BoardTopicModerationEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class BoardTopicMovedEvent(_BoardTopicModerationEvent):
    old_category_id: BoardCategoryID
    old_category_title: str
    new_category_id: BoardCategoryID
    new_category_title: str


# posting


@dataclass(frozen=True, kw_only=True)
class _BoardPostingEvent(_BoardEvent):
    posting_id: PostingID
    posting_creator: User
    topic_id: TopicID
    topic_title: str
    url: str


@dataclass(frozen=True, kw_only=True)
class _BoardPostingModerationEvent(_BoardPostingEvent):
    moderator: User


@dataclass(frozen=True, kw_only=True)
class BoardPostingCreatedEvent(_BoardPostingEvent):
    topic_muted: bool


@dataclass(frozen=True, kw_only=True)
class BoardPostingUpdatedEvent(_BoardPostingEvent):
    editor: User


@dataclass(frozen=True, kw_only=True)
class BoardPostingHiddenEvent(_BoardPostingModerationEvent):
    pass


@dataclass(frozen=True, kw_only=True)
class BoardPostingUnhiddenEvent(_BoardPostingModerationEvent):
    pass
