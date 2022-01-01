"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import byceps.services.party.service as party_service


def test_index(party_admin_client, party):
    url = '/admin/parties/'
    response = party_admin_client.get(url)
    assert response.status_code == 200


def test_index_for_brand(party_admin_client, brand, party):
    url = f'/admin/parties/brands/{brand.id}'
    response = party_admin_client.get(url)
    assert response.status_code == 200


def test_view(party_admin_client, party):
    url = f'/admin/parties/parties/{party.id}'
    response = party_admin_client.get(url)
    assert response.status_code == 200


def test_create_form(party_admin_client, brand):
    url = f'/admin/parties/for_brand/{brand.id}/create'
    response = party_admin_client.get(url)
    assert response.status_code == 200


def test_create(party_admin_client, brand):
    party_id = 'galant-2020'
    title = 'gaLANt 2020'
    max_ticket_quantity = 126

    assert party_service.find_party(party_id) is None

    url = f'/admin/parties/for_brand/{brand.id}'
    form_data = {
        'id': party_id,
        'title': title,
        # Dates/times are local in UTC+02:00.
        'starts_on': '2020-09-18',
        'starts_at': '17:00',
        'ends_on': '2020-09-20',
        'ends_at': '13:00',
        'max_ticket_quantity': str(max_ticket_quantity),
    }
    response = party_admin_client.post(url, data=form_data)

    party = party_service.find_party(party_id)
    assert party is not None
    assert party.id == party_id
    assert party.starts_at == datetime(2020, 9, 18, 15, 0)  # UTC
    assert party.ends_at == datetime(2020, 9, 20, 11, 0)  # UTC
    assert party.max_ticket_quantity == max_ticket_quantity


def test_update_form(party_admin_client, party):
    url = f'/admin/parties/parties/{party.id}/update'
    response = party_admin_client.get(url)
    assert response.status_code == 200
