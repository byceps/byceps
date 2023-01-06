"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.site import site_service


def test_index(site_admin_client, site):
    url = '/admin/sites/'
    response = site_admin_client.get(url)
    assert response.status_code == 200


def test_view(site_admin_client, site):
    url = f'/admin/sites/sites/{site.id}'
    response = site_admin_client.get(url)
    assert response.status_code == 200


def test_create_form(site_admin_client, brand):
    url = f'/admin/sites/sites/create/for_brand/{brand.id}'
    response = site_admin_client.get(url)
    assert response.status_code == 200


def test_create(site_admin_client, brand):
    site_id = 'partysite-99'
    title = 'Party 99'
    server_name = 'www.party99.example'

    assert site_service.find_site(site_id) is None

    url = f'/admin/sites/sites/for_brand/{brand.id}'
    form_data = {
        'id': site_id,
        'title': title,
        'server_name': server_name,
        'news_channel_id': '',
        'board_id': '',
        'storefront_id': '',
    }
    response = site_admin_client.post(url, data=form_data)
    assert response.status_code == 302

    site = site_service.find_site(site_id)
    assert site is not None
    assert site.id == site_id
    assert site.title == title
    assert site.server_name == server_name
    assert site.news_channel_ids == frozenset()
    assert site.board_id is None
    assert site.storefront_id is None


def test_update_form(site_admin_client, site):
    url = f'/admin/sites/sites/{site.id}/update'
    response = site_admin_client.get(url)
    assert response.status_code == 200
