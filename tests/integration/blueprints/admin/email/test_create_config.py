"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import byceps.services.email.service as email_service

from tests.helpers import http_client


def test_create_minimal_config(admin_app, email_admin):
    config_id = 'acme-minimal'
    assert email_service.find_config(config_id) is None

    url = '/admin/email/configs'
    form_data = {
        'config_id': config_id,
        'sender_address': 'noreply@acme.example',
    }
    with http_client(admin_app, user_id=email_admin.id) as client:
        response = client.post(url, data=form_data)

    config = email_service.find_config(config_id)
    assert config is not None
    assert config.id == config_id
    assert config.sender is not None
    assert config.sender.address == 'noreply@acme.example'
    assert config.sender.name is None
    assert config.contact_address is None


def test_create_full_config(admin_app, email_admin):
    config_id = 'acme-full'
    assert email_service.find_config(config_id) is None

    url = '/admin/email/configs'
    form_data = {
        'config_id': config_id,
        'sender_address': 'noreply@acme.example',
        'sender_name': 'ACME Corp.',
        'contact_address': 'info@acme.example',
    }
    with http_client(admin_app, user_id=email_admin.id) as client:
        response = client.post(url, data=form_data)

    config = email_service.find_config(config_id)
    assert config is not None
    assert config.id == config_id
    assert config.sender is not None
    assert config.sender.address == 'noreply@acme.example'
    assert config.sender.name == 'ACME Corp.'
    assert config.contact_address == 'info@acme.example'
