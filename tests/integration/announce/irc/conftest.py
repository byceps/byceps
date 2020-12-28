"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.webhooks import service as webhook_service

from .helpers import CHANNEL_ORGA_LOG, CHANNEL_PUBLIC


@pytest.fixture(scope='module')
def webhook_settings():
    scopes_and_channels = [
        ('internal', CHANNEL_ORGA_LOG),
        ('public', CHANNEL_PUBLIC),
    ]
    scope_id = None
    format = 'weitersager'
    url = 'http://127.0.0.1:12345/'
    enabled = True

    webhooks = [
        webhook_service.create_outgoing_webhook(
            scope,
            scope_id,
            format,
            url,
            enabled,
            extra_fields={'channel': channel},
        )
        for scope, channel in scopes_and_channels
    ]

    yield

    for webhook in webhooks:
        webhook_service.delete_outgoing_webhook(webhook.id)


@pytest.fixture(scope='module')
def app(admin_app, webhook_settings):
    return admin_app
