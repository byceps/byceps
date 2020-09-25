"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import byceps.services.site.service as site_service

from tests.helpers import http_client


def test_index(admin_app, site_admin, site):
    url = '/admin/sites/'
    response = get_resource(admin_app, site_admin, url)
    assert response.status_code == 200


def test_view(admin_app, site_admin, site):
    url = f'/admin/sites/sites/{site.id}'
    response = get_resource(admin_app, site_admin, url)
    assert response.status_code == 200


def test_create_form(admin_app, site_admin, brand):
    url = f'/admin/sites/sites/create/for_brand/{brand.id}'
    response = get_resource(admin_app, site_admin, url)
    assert response.status_code == 200


def test_create(admin_app, site_admin, brand, email_config):
    site_id = 'partysite-99'
    title = 'Party 99'
    server_name = 'www.party99.example'

    assert site_service.find_site(site_id) is None

    url = f'/admin/sites/sites/for_brand/{brand.id}'
    form_data = {
        'id': site_id,
        'title': title,
        'server_name': server_name,
        'email_config_id': email_config.id,
        'news_channel_id': '',
        'board_id': '',
        'storefront_id': '',
    }
    response = post_resource(admin_app, site_admin, url, form_data)

    site = site_service.find_site(site_id)
    assert site is not None
    assert site.id == site_id
    assert site.title == title
    assert site.server_name == server_name
    assert site.email_config_id == email_config.id
    assert site.news_channel_id is None
    assert site.board_id is None
    assert site.storefront_id is None

    # Clean up.
    site_service.delete_site(site_id)


def test_update_form(admin_app, site_admin, site):
    url = f'/admin/sites/sites/{site.id}/update'
    response = get_resource(admin_app, site_admin, url)
    assert response.status_code == 200


# helpers


def get_resource(app, user, url):
    with http_client(app, user_id=user.id) as client:
        return client.get(url)


def post_resource(app, user, url, data):
    with http_client(app, user_id=user.id) as client:
        return client.post(url, data=data)
