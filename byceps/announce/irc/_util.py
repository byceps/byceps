"""
byceps.announce.irc.util
~~~~~~~~~~~~~~~~~~~~~~~~

Send messages to an IRC bot (Weitersager_) via HTTP.

.. _Weitersager: https://github.com/homeworkprod/weitersager

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import current_app

from ...events.base import _BaseEvent
from ...services.webhooks import service as webhook_service

from ..helpers import call_webhook
from ..visibility import get_visibilities


def send_message(
    event: _BaseEvent, webhook_format: str, scope: str, scope_id: str, text: str
) -> None:
    """Write the text to the channel(s) configured for this event type
    by sending it to the bot via HTTP.
    """
    visibilities = get_visibilities(event)
    if not visibilities:
        current_app.logger.warning(
            f'No visibility assigned for event type "{type(event)}".'
        )
        return

    scope_id = None

    webhooks = []
    for visibility in visibilities:
        scope = visibility.name

        webhooks.extend(
            webhook_service.get_enabled_outgoing_webhooks(
                scope, scope_id, webhook_format
            )
        )

    if not webhooks:
        current_app.logger.warning(
            f'No enabled IRC webhooks found. Not sending message to IRC.'
        )
        return

    # Stable order is easier to test.
    webhooks.sort(key=lambda wh: wh.extra_fields['channel'])

    for webhook in webhooks:
        call_webhook(webhook, text)
