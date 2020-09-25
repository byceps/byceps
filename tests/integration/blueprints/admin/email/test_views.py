"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import byceps.services.email.service as email_service

from tests.helpers import http_client


def test_index(admin_app, email_admin, site):
    url = '/admin/email/configs'
    response = get_resource(admin_app, email_admin, url)
    assert response.status_code == 200


def test_create_form(admin_app, email_admin):
    url = '/admin/email/configs/create'
    response = get_resource(admin_app, email_admin, url)
    assert response.status_code == 200


def test_update_form(admin_app, email_admin, email_config):
    url = f'/admin/email/configs/{email_config.id}/update'
    response = get_resource(admin_app, email_admin, url)
    assert response.status_code == 200


# helpers


def get_resource(app, user, url):
    with http_client(app, user_id=user.id) as client:
        return client.get(url)
