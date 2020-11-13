"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import byceps.services.email.service as email_service


def test_index(email_admin_client, site):
    url = '/admin/email/configs'
    response = email_admin_client.get(url)
    assert response.status_code == 200


def test_create_form(email_admin_client):
    url = '/admin/email/configs/create'
    response = email_admin_client.get(url)
    assert response.status_code == 200


def test_update_form(email_admin_client, email_config):
    url = f'/admin/email/configs/{email_config.id}/update'
    response = email_admin_client.get(url)
    assert response.status_code == 200
