"""
byceps.announce.irc.board
~~~~~~~~~~~~~~~~~~~~~~~~~

Announce board events on IRC.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

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

from ..common import board
from ..helpers import send_message


def announce_board_topic_created(
    event: BoardTopicCreated, webhook_format: str
) -> None:
    """Announce that someone has created a board topic."""
    text = board.assemble_text_for_board_topic_created(event, webhook_format)

    send_board_message(event, webhook_format, text)


def announce_board_topic_hidden(
    event: BoardTopicHidden, webhook_format: str
) -> None:
    """Announce that a moderator has hidden a board topic."""
    text = board.assemble_text_for_board_topic_hidden(event, webhook_format)

    send_board_message(event, webhook_format, text)


def announce_board_topic_unhidden(
    event: BoardTopicUnhidden, webhook_format: str
) -> None:
    """Announce that a moderator has made a board topic visible again."""
    text = board.assemble_text_for_board_topic_unhidden(event, webhook_format)

    send_board_message(event, webhook_format, text)


def announce_board_topic_locked(
    event: BoardTopicLocked, webhook_format: str
) -> None:
    """Announce that a moderator has locked a board topic."""
    text = board.assemble_text_for_board_topic_locked(event, webhook_format)

    send_board_message(event, webhook_format, text)


def announce_board_topic_unlocked(
    event: BoardTopicUnlocked, webhook_format: str
) -> None:
    """Announce that a moderator has unlocked a board topic."""
    text = board.assemble_text_for_board_topic_unlocked(event, webhook_format)

    send_board_message(event, webhook_format, text)


def announce_board_topic_pinned(
    event: BoardTopicPinned, webhook_format: str
) -> None:
    """Announce that a moderator has pinned a board topic."""
    text = board.assemble_text_for_board_topic_pinned(event, webhook_format)

    send_board_message(event, webhook_format, text)


def announce_board_topic_unpinned(
    event: BoardTopicUnpinned, webhook_format: str
) -> None:
    """Announce that a moderator has unpinned a board topic."""
    text = board.assemble_text_for_board_topic_unpinned(event, webhook_format)

    send_board_message(event, webhook_format, text)


def announce_board_topic_moved(
    event: BoardTopicMoved, webhook_format: str
) -> None:
    """Announce that a moderator has moved a board topic to another category."""
    text = board.assemble_text_for_board_topic_moved(event, webhook_format)

    send_board_message(event, webhook_format, text)


def announce_board_posting_created(
    event: BoardPostingCreated, webhook_format: str
) -> None:
    """Announce that someone has created a board posting."""
    if event.topic_muted:
        return

    text = board.assemble_text_for_board_posting_created(event, webhook_format)

    send_board_message(event, webhook_format, text)


def announce_board_posting_hidden(
    event: BoardPostingHidden, webhook_format: str
) -> None:
    """Announce that a moderator has hidden a board posting."""
    text = board.assemble_text_for_board_posting_hidden(event, webhook_format)

    send_board_message(event, webhook_format, text)


def announce_board_posting_unhidden(
    event: BoardPostingUnhidden, webhook_format: str
) -> None:
    """Announce that a moderator has made a board posting visible again."""
    text = board.assemble_text_for_board_posting_unhidden(event, webhook_format)

    send_board_message(event, webhook_format, text)


# helpers


def send_board_message(
    event: _BoardEvent, webhook_format: str, text: str
) -> None:
    scope = 'board'
    scope_id = str(event.board_id)

    send_message(event, webhook_format, scope, scope_id, text)
