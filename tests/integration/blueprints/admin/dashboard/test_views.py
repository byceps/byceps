"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from tests.helpers import log_in_user


def test_view_global(dashboard_admin_client):
    url = '/admin/dashboard'
    response = dashboard_admin_client.get(url)
    assert response.status_code == 200


def test_view_brand(dashboard_admin_client, brand):
    url = f'/admin/dashboard/brands/{brand.id}'
    response = dashboard_admin_client.get(url)
    assert response.status_code == 200


def test_view_party(dashboard_admin_client, party):
    url = f'/admin/dashboard/parties/{party.id}'
    response = dashboard_admin_client.get(url)
    assert response.status_code == 200


def test_view_site(dashboard_admin_client, site):
    url = f'/admin/dashboard/sites/{site.id}'
    response = dashboard_admin_client.get(url)
    assert response.status_code == 200


@pytest.fixture(scope='package')
def dashboard_admin(make_admin):
    permission_ids = {
        'admin.access',
        'brand.view',
        'party.view',
        'site.view',
    }
    admin = make_admin(permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def dashboard_admin_client(make_client, admin_app, dashboard_admin):
    return make_client(admin_app, user_id=dashboard_admin.id)
