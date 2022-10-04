"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.brand import brand_service
from byceps.services.email import email_config_service


def test_index(brand_admin_client, brand):
    url = '/admin/brands/'
    response = brand_admin_client.get(url)
    assert response.status_code == 200


def test_view(brand_admin_client, brand):
    url = f'/admin/brands/brands/{brand.id}'
    response = brand_admin_client.get(url)
    assert response.status_code == 200


def test_create_form(brand_admin_client):
    url = '/admin/brands/create'
    response = brand_admin_client.get(url)
    assert response.status_code == 200


def test_create(brand_admin_client):
    brand_id = 'galant'
    title = 'gaLANt'

    assert brand_service.find_brand(brand_id) is None

    url = '/admin/brands/'
    form_data = {
        'id': brand_id,
        'title': title,
    }
    response = brand_admin_client.post(url, data=form_data)
    assert response.status_code == 302

    brand = brand_service.find_brand(brand_id)
    assert brand is not None
    assert brand.id == brand_id
    assert brand.title == title

    email_config = email_config_service.get_config(brand.id)
    assert email_config.sender is not None
    assert email_config.sender.address == 'noreply@galant.example'
    assert email_config.sender.name == 'gaLANt'
    assert email_config.contact_address == 'info@galant.example'


def test_update_form(brand_admin_client, brand):
    url = f'/admin/brands/brands/{brand.id}/update'
    response = brand_admin_client.get(url)
    assert response.status_code == 200


def test_email_config_update_form(brand_admin_client, email_config):
    url = f'/admin/brands/brands/{email_config.brand_id}/email_config/update'
    response = brand_admin_client.get(url)
    assert response.status_code == 200
