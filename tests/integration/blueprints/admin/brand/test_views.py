"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import byceps.services.brand.service as brand_service

from tests.helpers import http_client


def test_index(admin_app, brand_admin, brand):
    url = '/admin/brands/'
    response = get_resource(admin_app, brand_admin, url)
    assert response.status_code == 200


def test_view(admin_app, brand_admin, brand):
    url = f'/admin/brands/brands/{brand.id}'
    response = get_resource(admin_app, brand_admin, url)
    assert response.status_code == 200


def test_create_form(admin_app, brand_admin):
    url = '/admin/brands/create'
    response = get_resource(admin_app, brand_admin, url)
    assert response.status_code == 200


def test_create(admin_app, brand_admin):
    brand_id = 'galant'
    title = 'gaLANt'

    assert brand_service.find_brand(brand_id) is None

    url = '/admin/brands/'
    form_data = {
        'id': brand_id,
        'title': title,
    }
    response = post_resource(admin_app, brand_admin, url, form_data)

    brand = brand_service.find_brand(brand_id)
    assert brand is not None
    assert brand.id == brand_id
    assert brand.title == title

    # Clean up.
    brand_service.delete_brand(brand_id)


def test_update_form(admin_app, brand_admin, brand):
    url = f'/admin/brands/brands/{brand.id}/update'
    response = get_resource(admin_app, brand_admin, url)
    assert response.status_code == 200


# helpers


def get_resource(app, user, url):
    with http_client(app, user_id=user.id) as client:
        return client.get(url)


def post_resource(app, user, url, data):
    with http_client(app, user_id=user.id) as client:
        return client.post(url, data=data)
