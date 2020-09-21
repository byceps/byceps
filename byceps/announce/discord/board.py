"""
byceps.announce.discord.board
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce board events on Discord via its webhooks API.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Optional

from flask import current_app
import requests

from ...events.board import BoardPostingCreated, BoardTopicCreated
from ...services.board import board_service
from ...services.board.transfer.models import BoardID
from ...services.brand import settings_service as brand_settings_service
from ...signals import board as board_signals
from ...typing import BrandID
from ...util.jobqueue import enqueue

from ..helpers import get_screen_name_or_fallback


# This is a pretty basic implementation that only supports a single
# webhook and that fetches its configuration from a brand's setting.
# For now, some customization is necessary to post announcements
# (especially for different brands, or even different parties) to
# different webhooks (i.e. effectively Discord channels).


def send_message(board_id: BoardID, text: str) -> None:
    """Send text to the webhook API.

    The endpoint URL already includes the target channel.
    """
    board = board_service.find_board(board_id)
    if not board:
        current_app.logger.warning(
            f'Unknown board ID "{board_id}". Not sending message to Discord.'
        )
        return

    brand_id = board.brand_id

    if not _is_enabled(brand_id):
        current_app.logger.warning('Announcements on Discord are disabled.')
        return

    url = _get_webhook_url(brand_id)
    if not url:
        current_app.logger.warning(
            'No webhook URL configured for announcements on Discord.'
        )
        return

    text_prefix = _get_text_prefix(brand_id)
    if text_prefix:
        text = text_prefix + text

    data = {'content': text}

    requests.post(url, json=data)  # Ignore response code for now.


def _is_enabled(brand_id: BrandID) -> bool:
    """Return `true' if announcements on Discord are enabled."""
    value = brand_settings_service.find_setting_value(
        brand_id, 'announce_discord_enabled'
    )
    return value == 'true'


def _get_webhook_url(brand_id: BrandID) -> str:
    """Return the configured webhook URL."""
    return brand_settings_service.find_setting_value(
        brand_id, 'announce_discord_webhook_url'
    )


def _get_text_prefix(brand_id: BrandID) -> Optional[str]:
    """Return the configured text prefix."""
    return brand_settings_service.find_setting_value(
        brand_id, 'announce_discord_text_prefix'
    )


# board events


# Note: URLs are wrapped in `<…>` because that prevents
#       preview embedding on Discord.


@board_signals.topic_created.connect
def _on_board_topic_created(sender, *, event: BoardTopicCreated = None) -> None:
    enqueue(announce_board_topic_created, event)


def announce_board_topic_created(event: BoardTopicCreated) -> None:
    """Announce that someone has created a board topic."""
    topic_creator_screen_name = get_screen_name_or_fallback(
        event.topic_creator_screen_name
    )

    text = (
        f'{topic_creator_screen_name} hat das Thema '
        f'"{event.topic_title}" erstellt: <{event.url}>'
    )

    send_message(event.board_id, text)


@board_signals.posting_created.connect
def _on_board_posting_created(
    sender, *, event: BoardPostingCreated = None
) -> None:
    enqueue(announce_board_posting_created, event)


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

    send_message(event.board_id, text)
