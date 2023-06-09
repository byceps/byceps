#!/usr/bin/env python

"""Wish orgas a happy birthday.

Meant to be called by a daily cronjob or similar mechanism.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

import click

from byceps.announce.announce import assemble_announcement_request, call_webhook
from byceps.services.orga import orga_birthday_service
from byceps.services.webhooks import webhook_service
from byceps.services.webhooks.models import OutgoingWebhook, WebhookID

from _util import call_with_app_context


def validate_webhook_id(ctx, param, webhook_id_value: str) -> OutgoingWebhook:
    try:
        webhook_id = WebhookID(UUID(webhook_id_value))
    except ValueError as exc:
        raise click.BadParameter(
            f'Invalid webhook ID "{webhook_id_value}": {exc}'
        ) from exc

    webhook = webhook_service.find_webhook(webhook_id)

    if webhook is None:
        raise click.BadParameter(f'Unknown webhook ID "{webhook_id}".')

    return webhook


@click.command()
@click.argument('webhook', callback=validate_webhook_id)
def execute(webhook: OutgoingWebhook) -> None:
    users = orga_birthday_service.get_orgas_with_birthday_today()

    for user in users:
        text = f'Happy Birthday, {user.screen_name}! 🥳'
        announcement_request = assemble_announcement_request(webhook, text)
        call_webhook(webhook, announcement_request)


if __name__ == '__main__':
    call_with_app_context(execute)
