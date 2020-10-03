"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.helpers import http_client


def test_ticket_index(admin_app, party, ticketing_admin, ticket):
    url = f'/admin/ticketing/tickets/for_party/{party.id}'
    response = get_resource(admin_app, ticketing_admin, url)
    assert response.status_code == 200


def test_ticket_view(admin_app, ticketing_admin, ticket):
    url = f'/admin/ticketing/tickets/{ticket.id}'
    response = get_resource(admin_app, ticketing_admin, url)
    assert response.status_code == 200


def test_appoint_user_form(admin_app, ticketing_admin, ticket):
    url = f'/admin/ticketing/tickets/{ticket.id}/appoint_user'
    response = get_resource(admin_app, ticketing_admin, url)
    assert response.status_code == 200


def test_bundle_index(admin_app, party, ticketing_admin, bundle):
    url = f'/admin/ticketing/bundles/for_party/{party.id}'
    response = get_resource(admin_app, ticketing_admin, url)
    assert response.status_code == 200


def test_bundle_view(admin_app, ticketing_admin, bundle):
    url = f'/admin/ticketing/bundles/{bundle.id}'
    response = get_resource(admin_app, ticketing_admin, url)
    assert response.status_code == 200


# helpers


def get_resource(app, user, url):
    with http_client(app, user_id=user.id) as client:
        return client.get(url)
