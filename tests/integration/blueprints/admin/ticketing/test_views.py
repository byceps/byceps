"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""


def test_ticket_index(party, ticketing_admin_client, ticket):
    url = f'/admin/ticketing/tickets/for_party/{party.id}'
    response = ticketing_admin_client.get(url)
    assert response.status_code == 200


def test_ticket_view(ticketing_admin_client, ticket):
    url = f'/admin/ticketing/tickets/{ticket.id}'
    response = ticketing_admin_client.get(url)
    assert response.status_code == 200


def test_appoint_user_form(ticketing_admin_client, ticket):
    url = f'/admin/ticketing/tickets/{ticket.id}/appoint_user'
    response = ticketing_admin_client.get(url)
    assert response.status_code == 200


def test_bundle_index(party, ticketing_admin_client, bundle):
    url = f'/admin/ticketing/bundles/for_party/{party.id}'
    response = ticketing_admin_client.get(url)
    assert response.status_code == 200


def test_bundle_view(ticketing_admin_client, bundle):
    url = f'/admin/ticketing/bundles/{bundle.id}'
    response = ticketing_admin_client.get(url)
    assert response.status_code == 200
