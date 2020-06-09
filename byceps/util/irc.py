"""
byceps.util.irc
~~~~~~~~~~~~~~~

Send IRC messages to a bot via HTTP.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from time import sleep
from typing import List

from flask import current_app
import requests


DEFAULT_BOT_URL = 'http://127.0.0.1:12345/'
DEFAULT_ENABLED = False
DEFAULT_DELAY_IN_SECONDS = 2
DEFAULT_TEXT_PREFIX = '[BYCEPS] '


def send_message(channels: List[str], text: str) -> None:
    """Write the text to the channels by sending it to the bot via HTTP."""
    enabled = current_app.config.get('ANNOUNCE_IRC_ENABLED', DEFAULT_ENABLED)
    if not enabled:
        current_app.logger.warning('Announcements on IRC are disabled.')
        return

    text_prefix = current_app.config.get(
        'ANNOUNCE_IRC_TEXT_PREFIX', DEFAULT_TEXT_PREFIX
    )

    text = text_prefix + text

    url = current_app.config.get('IRC_BOT_URL', DEFAULT_BOT_URL)
    data = {'channels': channels, 'text': text}

    # Delay a bit as an attempt to avoid getting kicked from server
    # because of flooding.
    delay = int(
        current_app.config.get('ANNOUNCE_IRC_DELAY', DEFAULT_DELAY_IN_SECONDS)
    )
    sleep(delay)

    requests.post(url, json=data)  # Ignore response code for now.
