"""
byceps.announce.discord.board
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce board events on Discord.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.board import _BoardEvent, BoardPostingCreated, BoardTopicCreated

from ..helpers import get_screen_name_or_fallback

from ._util import send_message


# Note: URLs are wrapped in `<…>` because that prevents
#       preview embedding on Discord.


def announce_board_topic_created(event: BoardTopicCreated) -> None:
    """Announce that someone has created a board topic."""
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )

    text = (
        f'{topic_creator_screen_name} hat das Thema '
        f'"{event.topic_title}" erstellt: <{event.url}>'
    )

    send_board_message(event, text)


def announce_board_posting_created(event: BoardPostingCreated) -> None:
    """Announce that someone has created a board posting."""
    if event.topic_muted:
        return

    posting_creator_screen_name = get_screen_name_or_fallback(
        event.posting_creator_screen_name
    )

    text = (
        f'{posting_creator_screen_name} hat auf das Thema '
        f'"{event.topic_title}" geantwortet: <{event.url}>'
    )

    send_board_message(event, text)


# helpers


def send_board_message(event: _BoardEvent, text: str) -> None:
    scope = 'board'
    scope_id = str(event.board_id)

    send_message(event, scope, scope_id, text)
