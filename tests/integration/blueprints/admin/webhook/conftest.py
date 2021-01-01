"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from tests.helpers import login_user


@pytest.fixture(scope='package')
def webhook_admin(make_admin):
    permission_ids = {
        'admin.access',
        'webhook.administrate',
        'webhook.view',
    }
    admin = make_admin('WebhookAdmin', permission_ids)
    login_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def webhook_admin_client(make_client, admin_app, webhook_admin):
    return make_client(admin_app, user_id=webhook_admin.id)
