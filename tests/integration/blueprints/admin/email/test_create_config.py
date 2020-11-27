"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import byceps.services.email.service as email_service


def test_create_minimal_config(email_admin_client, make_brand):
    brand = make_brand('acme-create-1', 'ACME create test 1')

    config_id = 'acme-minimal'
    assert email_service.find_config(config_id) is None

    url = '/admin/email/configs'
    form_data = {
        'config_id': config_id,
        'brand_id': brand.id,
        'sender_address': 'noreply@acme.example',
    }
    response = email_admin_client.post(url, data=form_data)

    config = email_service.find_config(config_id)
    assert config is not None
    assert config.id == config_id
    assert config.brand_id == brand.id
    assert config.sender is not None
    assert config.sender.address == 'noreply@acme.example'
    assert config.sender.name is None
    assert config.contact_address is None

    # Clean up.
    email_service.delete_config(config_id)


def test_create_full_config(email_admin_client, make_brand):
    brand = make_brand('acme-create-2', 'ACME create test 2')

    config_id = 'acme-full'
    assert email_service.find_config(config_id) is None

    url = '/admin/email/configs'
    form_data = {
        'config_id': config_id,
        'brand_id': brand.id,
        'sender_address': 'noreply@acme.example',
        'sender_name': 'ACME Corp.',
        'contact_address': 'info@acme.example',
    }
    response = email_admin_client.post(url, data=form_data)

    config = email_service.find_config(config_id)
    assert config is not None
    assert config.id == config_id
    assert config.brand_id == brand.id
    assert config.sender is not None
    assert config.sender.address == 'noreply@acme.example'
    assert config.sender.name == 'ACME Corp.'
    assert config.contact_address == 'info@acme.example'

    # Clean up.
    email_service.delete_config(config_id)
