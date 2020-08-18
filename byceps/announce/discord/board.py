"""
byceps.announce.discord.board
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Announce board events on Discord via its webhooks API.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import current_app
import requests

from ...events.board import BoardPostingCreated, BoardTopicCreated
from ...services.board import (
    posting_query_service as board_posting_query_service,
    topic_query_service as board_topic_query_service,
)
from ...services.brand import settings_service as brand_settings_service
from ...services.user import service as user_service
from ...signals import board as board_signals
from ...util.jobqueue import enqueue


# This is a pretty basic implementation that only supports a single
# webhook and that fetches its configuration from a brand's setting.
# For now, some customization is necessary to post announcements
# (especially for different brands, or even different parties) to
# different webhooks (i.e. effectively Discord channels).


BRAND_ID = 'YOUR-BRAND-HERE'


def send_message(text: str) -> None:
    """Send text to the webhook API.

    The endpoint URL already includes the target channel.
    """
    if not _is_enabled():
        current_app.logger.warning('Announcements on Discord are disabled.')
        return

    url = _get_webhook_url()
    if not url:
        current_app.logger.warning(
            'No webhook URL configured for announcements on Discord.'
        )
        return

    data = {'content': text}

    requests.post(url, json=data)  # Ignore response code for now.


def _is_enabled() -> bool:
    """Return `true' if announcements on Discord are enabled."""
    value = brand_settings_service.find_setting_value(
        BRAND_ID, 'announce_discord_enabled'
    )
    return value == 'true'


def _get_webhook_url() -> str:
    """Return the configured webhook URL."""
    return brand_settings_service.find_setting_value(
        BRAND_ID, 'announce_discord_webhook_url'
    )


# board events


# Note: URLs are wrapped in `<…>` because that prevents
#       preview embedding on Discord.


@board_signals.topic_created.connect
def _on_board_topic_created(sender, *, event: BoardTopicCreated = None) -> None:
    enqueue(announce_board_topic_created, event)


def announce_board_topic_created(event: BoardTopicCreated) -> None:
    """Announce that someone has created a board topic."""
    topic = board_topic_query_service.find_topic_by_id(event.topic_id)
    creator_screen_name = user_service.find_screen_name(topic.creator_id)

    text = (
        f'[Forum] {creator_screen_name} hat das Thema "{event.topic_title}" '
        f'erstellt: <{event.url}>'
    )

    send_message(text)


@board_signals.posting_created.connect
def _on_board_posting_created(
    sender, *, event: BoardPostingCreated = None
) -> None:
    enqueue(announce_board_posting_created, event)


def announce_board_posting_created(event: BoardPostingCreated) -> None:
    """Announce that someone has created a board posting."""
    posting = board_posting_query_service.find_posting_by_id(event.posting_id)
    creator_screen_name = user_service.find_screen_name(posting.creator_id)

    if event.topic_muted:
        return

    text = (
        f'[Forum] {creator_screen_name} hat auf das Thema '
        f'"{event.topic_title}" geantwortet: <{event.url}>'
    )

    send_message(text)
