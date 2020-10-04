"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

import byceps.services.shop.shop.service as shop_service

from tests.helpers import login_user


@pytest.fixture(scope='package')
def shop_admin(make_admin):
    permission_ids = {
        'admin.access',
        'shop.create',
    }
    admin = make_admin('ShopAdmin', permission_ids)
    login_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def shop_admin_client(make_client, admin_app, shop_admin):
    return make_client(admin_app, user_id=shop_admin.id)


def test_create_shop(email_config, shop_admin_client):
    shop_id = 'acme'
    assert shop_service.find_shop(shop_id) is None

    url = '/admin/shop/shop/shops'
    form_data = {
        'id': shop_id,
        'title': 'ACME',
        'email_config_id': email_config.id,
    }
    response = shop_admin_client.post(url, data=form_data)

    shop = shop_service.find_shop(shop_id)
    assert shop is not None
    assert shop.id == shop_id
    assert shop.title == 'ACME'
    assert shop.email_config_id == email_config.id
