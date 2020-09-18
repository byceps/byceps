"""
byceps.util.irc
~~~~~~~~~~~~~~~

Send IRC messages to a bot via HTTP.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from time import sleep
from typing import Any, Optional

from flask import current_app
import requests


DEFAULT_WEBHOOK_URL = 'http://127.0.0.1:12345/'
DEFAULT_ENABLED = False
DEFAULT_DELAY_IN_SECONDS = 2
DEFAULT_TEXT_PREFIX = '[BYCEPS] '


def send_message(channel: str, text: str) -> None:
    """Write the text to the channel by sending it to the bot via HTTP."""
    if not _is_enabled():
        current_app.logger.warning('Announcements on IRC are disabled.')
        return

    url = _get_webhook_url()
    if not url:
        current_app.logger.warning(
            'No webhook URL configured for announcements on IRC.'
        )
        return

    text_prefix = _get_text_prefix()
    if text_prefix:
        text = text_prefix + text

    data = {'channel': channel, 'text': text}

    # Delay a bit as an attempt to avoid getting kicked from server
    # because of flooding.
    delay = _get_delay()
    sleep(delay)

    requests.post(url, json=data)  # Ignore response code for now.


def _is_enabled() -> bool:
    """Return `true' if announcements on IRC are enabled."""
    return _get_config_value('ANNOUNCE_IRC_ENABLED', DEFAULT_ENABLED)


def _get_webhook_url() -> str:
    """Return the configured webhook URL."""
    return _get_config_value('ANNOUNCE_IRC_WEBHOOK_URL', DEFAULT_WEBHOOK_URL)


def _get_text_prefix() -> Optional[str]:
    """Return the configured text prefix."""
    return _get_config_value('ANNOUNCE_IRC_TEXT_PREFIX', DEFAULT_TEXT_PREFIX)


def _get_delay() -> int:
    """Return the configured delay."""
    value = _get_config_value('ANNOUNCE_IRC_DELAY', DEFAULT_DELAY_IN_SECONDS)

    try:
        value = int(value)
    except (TypeError, ValueError) as e:
        current_app.logger.warning(
            f'Invalid delay value configured for announcements on IRC: {e}'
        )
        return DEFAULT_DELAY_IN_SECONDS

    return value


def _get_config_value(key: str, default_value: Any) -> Optional[Any]:
    return current_app.config.get(key, default_value)
