"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.webhooks import service as webhook_service


@pytest.fixture(scope='module')
def webhook_settings():
    scope = 'any'
    scope_id = None
    format = 'weitersager'
    url = 'http://127.0.0.1:12345/'
    enabled = True

    webhook = webhook_service.create_outgoing_webhook(
        scope, scope_id, format, url, enabled
    )

    yield

    webhook_service.delete_outgoing_webhook(webhook.id)


@pytest.fixture(scope='module')
def app(admin_app, webhook_settings):
    return admin_app
