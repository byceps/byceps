"""
byceps.util.irc
~~~~~~~~~~~~~~~

Send messages to an IRC bot (Weitersager_) via HTTP.

.. _Weitersager: https://github.com/homeworkprod/weitersager

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask import current_app
import requests

from ..services.webhooks import service as webhook_service


def send_message(channel: str, text: str) -> None:
    """Write the text to the channel by sending it to the bot via HTTP."""
    scope = 'any'
    scope_id = None
    format = 'weitersager'

    webhook = webhook_service.find_enabled_outgoing_webhook(scope, scope_id, format)

    if webhook is None:
        current_app.logger.warning(
            f'No enabled IRC webhook found. Not sending message to IRC.'
        )
        return

    text_prefix = webhook.text_prefix
    if text_prefix:
        text = text_prefix + text

    data = {'channel': channel, 'text': text}

    requests.post(webhook.url, json=data)  # Ignore response code for now.
