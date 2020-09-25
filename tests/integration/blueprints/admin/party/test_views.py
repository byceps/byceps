"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

import byceps.services.party.service as party_service

from tests.helpers import http_client


def test_index(admin_app, party_admin, party):
    url = '/admin/parties/'
    response = get_resource(admin_app, party_admin, url)
    assert response.status_code == 200


def test_index_for_brand(admin_app, party_admin, brand, party):
    url = f'/admin/parties/brands/{brand.id}'
    response = get_resource(admin_app, party_admin, url)
    assert response.status_code == 200


def test_view(admin_app, party_admin, party):
    url = f'/admin/parties/parties/{party.id}'
    response = get_resource(admin_app, party_admin, url)
    assert response.status_code == 200


def test_create_form(admin_app, party_admin, brand):
    url = f'/admin/parties/for_brand/{brand.id}/create'
    response = get_resource(admin_app, party_admin, url)
    assert response.status_code == 200


def test_create(admin_app, party_admin, brand):
    party_id = 'galant-2020'
    title = 'gaLANt 2020'
    max_ticket_quantity = 126

    assert party_service.find_party(party_id) is None

    url = f'/admin/parties/for_brand/{brand.id}'
    form_data = {
        'id': party_id,
        'title': title,
        'starts_at': '18.09.2020 17:00',  # UTC+02:00
        'ends_at': '20.09.2020 13:00',  # UTC+02:00
        'max_ticket_quantity': str(max_ticket_quantity),
    }
    response = post_resource(admin_app, party_admin, url, form_data)

    party = party_service.find_party(party_id)
    assert party is not None
    assert party.id == party_id
    assert party.starts_at == datetime(2020, 9, 18, 15, 0)  # UTC
    assert party.ends_at == datetime(2020, 9, 20, 11, 0)  # UTC
    assert party.max_ticket_quantity == max_ticket_quantity

    # Clean up.
    party_service.delete_party(party_id)


def test_update_form(admin_app, party_admin, party):
    url = f'/admin/parties/parties/{party.id}/update'
    response = get_resource(admin_app, party_admin, url)
    assert response.status_code == 200


# helpers


def get_resource(app, user, url):
    with http_client(app, user_id=user.id) as client:
        return client.get(url)


def post_resource(app, user, url, data):
    with http_client(app, user_id=user.id) as client:
        return client.post(url, data=data)
