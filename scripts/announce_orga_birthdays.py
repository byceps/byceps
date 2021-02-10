#!/usr/bin/env python

"""Wish orgas a happy birthday.

Meant to be called by a daily cronjob or similar mechanism.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.announce.helpers import call_webhook
from byceps.services.orga import birthday_service
from byceps.services.webhooks import service as webhook_service
from byceps.services.webhooks.transfer.models import OutgoingWebhook, WebhookID
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context


def validate_webhook_id(ctx, param, webhook_id: WebhookID) -> OutgoingWebhook:
    webhook = webhook_service.find_webhook(webhook_id)

    if webhook is None:
        raise click.BadParameter(f'Unknown webhook ID "{webhook_id}".')

    return webhook


@click.command()
@click.argument('webhook', callback=validate_webhook_id)
def execute(webhook: OutgoingWebhook):
    users = birthday_service.get_orgas_with_birthday_today()

    for user in users:
        text = f'Happy Birthday, {user.screen_name}!'
        call_webhook(webhook, text)

    click.secho('Done.', fg='green')


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
