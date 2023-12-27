"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

BASE_URL = 'http://admin.acmecon.test'


def test_view_global(more_admin_client):
    url = f'{BASE_URL}/more/global'
    response = more_admin_client.get(url)
    assert response.status_code == 200


def test_view_brand(more_admin_client, brand):
    url = f'{BASE_URL}/more/brands/{brand.id}'
    response = more_admin_client.get(url)
    assert response.status_code == 200


def test_view_party(more_admin_client, party):
    url = f'{BASE_URL}/more/parties/{party.id}'
    response = more_admin_client.get(url)
    assert response.status_code == 200


def test_view_site(more_admin_client, site):
    url = f'{BASE_URL}/more/sites/{site.id}'
    response = more_admin_client.get(url)
    assert response.status_code == 200
