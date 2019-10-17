"""
byceps.events.board
~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass

from ..services.board.transfer.models import CategoryID, PostingID, TopicID
from ..typing import UserID


# topic


@dataclass(frozen=True)
class _BoardTopicEvent:
    topic_id: TopicID
    url: str


@dataclass(frozen=True)
class _BoardTopicModerationEvent(_BoardTopicEvent):
    moderator_id: UserID


@dataclass(frozen=True)
class BoardTopicCreated(_BoardTopicEvent):
    pass


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
    new_category_id: CategoryID


# posting


@dataclass(frozen=True)
class _BoardPostingEvent:
    posting_id: PostingID
    url: str


@dataclass(frozen=True)
class _BoardPostingModerationEvent:
    moderator_id: UserID


@dataclass(frozen=True)
class BoardPostingCreated(_BoardPostingEvent):
    pass


@dataclass(frozen=True)
class BoardPostingHidden(_BoardPostingModerationEvent):
    pass


@dataclass(frozen=True)
class BoardPostingUnhidden(_BoardPostingModerationEvent):
    pass
