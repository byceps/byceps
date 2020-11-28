"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import byceps.services.brand.service as brand_service


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

    brand = brand_service.find_brand(brand_id)
    assert brand is not None
    assert brand.id == brand_id
    assert brand.title == title

    # Clean up.
    brand_service.delete_brand(brand_id)


def test_update_form(brand_admin_client, brand):
    url = f'/admin/brands/brands/{brand.id}/update'
    response = brand_admin_client.get(url)
    assert response.status_code == 200


def test_email_config_update_form(brand_admin_client, email_config):
    url = f'/admin/brands/brands/{email_config.brand_id}/email_config/update'
    response = brand_admin_client.get(url)
    assert response.status_code == 200
