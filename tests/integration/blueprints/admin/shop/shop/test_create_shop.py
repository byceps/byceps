"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.shop import shop_service

from tests.helpers import log_in_user


@pytest.fixture(scope='package')
def shop_admin(make_admin):
    permission_ids = {
        'admin.access',
        'shop.create',
    }
    admin = make_admin(permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def shop_admin_client(make_client, admin_app, shop_admin):
    return make_client(admin_app, user_id=shop_admin.id)


def test_create_shop(make_brand, shop_admin_client):
    brand = make_brand(title='ACME')

    assert shop_service.find_shop_for_brand(brand.id) is None

    url = f'/admin/shop/shop/for_brand/{brand.id}'
    form_data = {'currency': 'EUR'}
    response = shop_admin_client.post(url, data=form_data)
    assert response.status_code == 302

    shop = shop_service.find_shop_for_brand(brand.id)
    assert shop is not None
    assert shop.id == brand.id
    assert shop.brand_id == brand.id
    assert shop.title == brand.title
