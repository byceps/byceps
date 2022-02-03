#!/usr/bin/env python

"""Wish orgas a happy birthday.

Meant to be called by a daily cronjob or similar mechanism.

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from uuid import UUID

import click
from flask.cli import with_appcontext

from byceps.announce.helpers import call_webhook
from byceps.services.orga import birthday_service
from byceps.services.webhooks import service as webhook_service
from byceps.services.webhooks.transfer.models import OutgoingWebhook, WebhookID


def validate_webhook_id(ctx, param, webhook_id_value: str) -> OutgoingWebhook:
    try:
        webhook_id = WebhookID(UUID(webhook_id_value))
    except ValueError as e:
        raise click.BadParameter(
            f'Invalid webhook ID "{webhook_id_value}": {e}'
        )

    webhook = webhook_service.find_webhook(webhook_id)

    if webhook is None:
        raise click.BadParameter(f'Unknown webhook ID "{webhook_id}".')

    return webhook


@click.command()
@click.argument('webhook', callback=validate_webhook_id)
@with_appcontext
def execute(webhook: OutgoingWebhook) -> None:
    users = birthday_service.get_orgas_with_birthday_today()

    for user in users:
        text = f'Happy Birthday, {user.screen_name}!'
        call_webhook(webhook, text)

    click.secho('Done.', fg='green')


if __name__ == '__main__':
    execute()
