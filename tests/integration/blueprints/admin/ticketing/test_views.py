"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

BASE_URL = 'http://admin.acmecon.test'


def test_ticket_index(party, ticketing_admin_client, ticket):
    url = f'{BASE_URL}/ticketing/tickets/for_party/{party.id}'
    response = ticketing_admin_client.get(url)
    assert response.status_code == 200


def test_ticket_view(ticketing_admin_client, ticket):
    url = f'{BASE_URL}/ticketing/tickets/{ticket.id}'
    response = ticketing_admin_client.get(url)
    assert response.status_code == 200


def test_appoint_user_form(ticketing_admin_client, ticket):
    url = f'{BASE_URL}/ticketing/tickets/{ticket.id}/appoint_user'
    response = ticketing_admin_client.get(url)
    assert response.status_code == 200


def test_bundle_index(party, ticketing_admin_client, bundle):
    url = f'{BASE_URL}/ticketing/bundles/for_party/{party.id}'
    response = ticketing_admin_client.get(url)
    assert response.status_code == 200


def test_bundle_view(ticketing_admin_client, bundle):
    url = f'{BASE_URL}/ticketing/bundles/{bundle.id}'
    response = ticketing_admin_client.get(url)
    assert response.status_code == 200


def test_category_index(ticketing_admin_client, party):
    url = f'{BASE_URL}/ticketing/categories/for_party/{party.id}'
    response = ticketing_admin_client.get(url)
    assert response.status_code == 200


def test_category_create_form(ticketing_admin_client, party):
    url = f'{BASE_URL}/ticketing/categories/for_party/{party.id}/create'
    response = ticketing_admin_client.get(url)
    assert response.status_code == 200


def test_category_update_form(ticketing_admin_client, category):
    url = f'{BASE_URL}/ticketing/categories/categories/{category.id}/update'
    response = ticketing_admin_client.get(url)
    assert response.status_code == 200
