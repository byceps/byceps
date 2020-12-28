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

from ._util import send_message


def announce_board_topic_created(event: BoardTopicCreated) -> None:
    """Announce that someone has created a board topic."""
    text = board.assemble_text_for_board_topic_created(event)

    send_board_message(event, text)


def announce_board_topic_hidden(event: BoardTopicHidden) -> None:
    """Announce that a moderator has hidden a board topic."""
    text = board.assemble_text_for_board_topic_hidden(event)

    send_board_message(event, text)


def announce_board_topic_unhidden(event: BoardTopicUnhidden) -> None:
    """Announce that a moderator has made a board topic visible again."""
    text = board.assemble_text_for_board_topic_unhidden(event)

    send_board_message(event, text)


def announce_board_topic_locked(event: BoardTopicLocked) -> None:
    """Announce that a moderator has locked a board topic."""
    text = board.assemble_text_for_board_topic_locked(event)

    send_board_message(event, text)


def announce_board_topic_unlocked(event: BoardTopicUnlocked) -> None:
    """Announce that a moderator has unlocked a board topic."""
    text = board.assemble_text_for_board_topic_unlocked(event)

    send_board_message(event, text)


def announce_board_topic_pinned(event: BoardTopicPinned) -> None:
    """Announce that a moderator has pinned a board topic."""
    text = board.assemble_text_for_board_topic_pinned(event)

    send_board_message(event, text)


def announce_board_topic_unpinned(event: BoardTopicUnpinned) -> None:
    """Announce that a moderator has unpinned a board topic."""
    text = board.assemble_text_for_board_topic_unpinned(event)

    send_board_message(event, text)


def announce_board_topic_moved(event: BoardTopicMoved) -> None:
    """Announce that a moderator has moved a board topic to another category."""
    text = board.assemble_text_for_board_topic_moved(event)

    send_board_message(event, text)


def announce_board_posting_created(event: BoardPostingCreated) -> None:
    """Announce that someone has created a board posting."""
    if event.topic_muted:
        return

    text = board.assemble_text_for_board_posting_created(event)

    send_board_message(event, text)


def announce_board_posting_hidden(event: BoardPostingHidden) -> None:
    """Announce that a moderator has hidden a board posting."""
    text = board.assemble_text_for_board_posting_hidden(event)

    send_board_message(event, text)


def announce_board_posting_unhidden(event: BoardPostingUnhidden) -> None:
    """Announce that a moderator has made a board posting visible again."""
    text = board.assemble_text_for_board_posting_unhidden(event)

    send_board_message(event, text)


# helpers


def send_board_message(event: _BoardEvent, text: str) -> None:
    scope = 'board'
    scope_id = str(event.board_id)

    send_message(event, scope, scope_id, text)
