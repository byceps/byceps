"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import byceps.services.email.service as email_service

from tests.helpers import http_client


def test_delete_config(admin_app, email_admin):
    config_id = 'kann-weg'

    assert email_service.create_config(config_id, 'noreply@acme.example')
    assert email_service.find_config(config_id) is not None

    url = f'/admin/email/configs/{config_id}'
    with http_client(admin_app, user_id=email_admin.id) as client:
        response = client.delete(url)

    assert email_service.find_config(config_id) is None
