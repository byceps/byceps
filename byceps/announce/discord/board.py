"""
byceps.announce.discord.board
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce board events on Discord.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.board import _BoardEvent, BoardPostingCreated, BoardTopicCreated

from ..common import board

from ._util import send_message


WEBHOOK_FORMAT = 'discord'


def announce_board_topic_created(event: BoardTopicCreated) -> None:
    """Announce that someone has created a board topic."""
    text = board.assemble_text_for_board_topic_created(event, WEBHOOK_FORMAT)

    send_board_message(event, text)


def announce_board_posting_created(event: BoardPostingCreated) -> None:
    """Announce that someone has created a board posting."""
    if event.topic_muted:
        return

    text = board.assemble_text_for_board_posting_created(event, WEBHOOK_FORMAT)

    send_board_message(event, text)


# helpers


def send_board_message(event: _BoardEvent, text: str) -> None:
    scope = 'board'
    scope_id = str(event.board_id)

    send_message(event, scope, scope_id, text)
