"""
byceps.announce.discord.board
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce board events on Discord.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from ...events.board import _BoardEvent, BoardPostingCreated, BoardTopicCreated
from ...services.webhooks.transfer.models import OutgoingWebhook

from ..common import board
from ..helpers import call_webhook, match_scope


def announce_board_topic_created(
    event: BoardTopicCreated, webhook: OutgoingWebhook
) -> None:
    """Announce that someone has created a board topic."""
    text = board.assemble_text_for_board_topic_created(event, webhook.format)

    send_board_message(event, webhook, text)


def announce_board_posting_created(
    event: BoardPostingCreated, webhook: OutgoingWebhook
) -> None:
    """Announce that someone has created a board posting."""
    if event.topic_muted:
        return

    text = board.assemble_text_for_board_posting_created(event, webhook.format)

    send_board_message(event, webhook, text)


# helpers


def send_board_message(
    event: _BoardEvent, webhook: OutgoingWebhook, text: str
) -> None:
    scope = 'board'
    scope_id = str(event.board_id)
    if not match_scope(webhook, scope, scope_id):
        return

    call_webhook(webhook, text)
