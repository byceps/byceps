"""
byceps.announce.handlers.board
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce board events.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from functools import wraps
from typing import Optional

from ...events.board import (
    _BoardEvent,
    BoardPostingCreated,
    BoardPostingHidden,
    BoardPostingUnhidden,
    BoardTopicCreated,
    BoardTopicHidden,
    BoardTopicLocked,
    BoardTopicMoved,
    BoardTopicPinned,
    BoardTopicUnhidden,
    BoardTopicUnlocked,
    BoardTopicUnpinned,
)
from ...services.webhooks.models import OutgoingWebhook

from ..helpers import Announcement
from ..helpers import matches_selectors
from ..text_assembly import board


def apply_selectors(handler):
    @wraps(handler)
    def wrapper(
        event: _BoardEvent, webhook: OutgoingWebhook
    ) -> Optional[Announcement]:
        board_id = str(event.board_id)
        if not matches_selectors(event, webhook, 'board_id', board_id):
            return None

        return handler(event, webhook)

    return wrapper


@apply_selectors
def announce_board_topic_created(
    event: BoardTopicCreated, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that someone has created a board topic."""
    text = board.assemble_text_for_board_topic_created(event, webhook.format)
    return Announcement(text)


@apply_selectors
def announce_board_topic_hidden(
    event: BoardTopicHidden, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has hidden a board topic."""
    text = board.assemble_text_for_board_topic_hidden(event, webhook.format)
    return Announcement(text)


@apply_selectors
def announce_board_topic_unhidden(
    event: BoardTopicUnhidden, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has made a board topic visible again."""
    text = board.assemble_text_for_board_topic_unhidden(event, webhook.format)
    return Announcement(text)


@apply_selectors
def announce_board_topic_locked(
    event: BoardTopicLocked, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has locked a board topic."""
    text = board.assemble_text_for_board_topic_locked(event, webhook.format)
    return Announcement(text)


@apply_selectors
def announce_board_topic_unlocked(
    event: BoardTopicUnlocked, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has unlocked a board topic."""
    text = board.assemble_text_for_board_topic_unlocked(event, webhook.format)
    return Announcement(text)


@apply_selectors
def announce_board_topic_pinned(
    event: BoardTopicPinned, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has pinned a board topic."""
    text = board.assemble_text_for_board_topic_pinned(event, webhook.format)
    return Announcement(text)


@apply_selectors
def announce_board_topic_unpinned(
    event: BoardTopicUnpinned, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has unpinned a board topic."""
    text = board.assemble_text_for_board_topic_unpinned(event, webhook.format)
    return Announcement(text)


@apply_selectors
def announce_board_topic_moved(
    event: BoardTopicMoved, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has moved a board topic to another category."""
    text = board.assemble_text_for_board_topic_moved(event, webhook.format)
    return Announcement(text)


@apply_selectors
def announce_board_posting_created(
    event: BoardPostingCreated, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that someone has created a board posting."""
    if event.topic_muted:
        return None

    text = board.assemble_text_for_board_posting_created(event, webhook.format)
    return Announcement(text)


@apply_selectors
def announce_board_posting_hidden(
    event: BoardPostingHidden, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has hidden a board posting."""
    text = board.assemble_text_for_board_posting_hidden(event, webhook.format)
    return Announcement(text)


@apply_selectors
def announce_board_posting_unhidden(
    event: BoardPostingUnhidden, webhook: OutgoingWebhook
) -> Optional[Announcement]:
    """Announce that a moderator has made a board posting visible again."""
    text = board.assemble_text_for_board_posting_unhidden(event, webhook.format)
    return Announcement(text)
