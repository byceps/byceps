"""
byceps.util.irc
~~~~~~~~~~~~~~~

Send IRC messages to a bot via HTTP.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from time import sleep
from typing import Any, List, Optional

from flask import current_app
import requests


DEFAULT_WEBHOOK_URL = 'http://127.0.0.1:12345/'
DEFAULT_ENABLED = False
DEFAULT_DELAY_IN_SECONDS = 2
DEFAULT_TEXT_PREFIX = '[BYCEPS] '


def send_message(channels: List[str], text: str) -> None:
    """Write the text to the channels by sending it to the bot via HTTP."""
    enabled = _get_config_value('ANNOUNCE_IRC_ENABLED', DEFAULT_ENABLED)
    if not enabled:
        current_app.logger.warning('Announcements on IRC are disabled.')
        return

    text_prefix = _get_config_value(
        'ANNOUNCE_IRC_TEXT_PREFIX', DEFAULT_TEXT_PREFIX
    )

    text = text_prefix + text

    url = _get_config_value('ANNOUNCE_IRC_WEBHOOK_URL', DEFAULT_WEBHOOK_URL)
    data = {'channels': channels, 'text': text}

    # Delay a bit as an attempt to avoid getting kicked from server
    # because of flooding.
    delay = int(
        _get_config_value('ANNOUNCE_IRC_DELAY', DEFAULT_DELAY_IN_SECONDS)
    )
    sleep(delay)

    requests.post(url, json=data)  # Ignore response code for now.


def _get_config_value(key: str, default_value: Any) -> Optional[Any]:
    return current_app.config.get(key, default_value)
