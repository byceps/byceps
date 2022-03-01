"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.ticketing import ticket_creation_service


def test_get_sale_stats(party, tickets, api_client, api_client_authz_header):
    url = f'/api/v1/ticketing/sale_stats/{party.id}'
    headers = [api_client_authz_header]

    response = api_client.get(url, headers=headers)

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.get_json() == {
        'tickets_max': 1348,
        'tickets_sold': 5,
    }


@pytest.fixture(scope='session')
def party(brand, make_party):
    party_id = 'for-the-stats'
    return make_party(
        brand.id, party_id, title=party_id, max_ticket_quantity=1348
    )


@pytest.fixture
def tickets(party, make_ticket_category, user):
    category = make_ticket_category(party.id, 'Normal')
    quantity = 5

    for i in range(quantity):
        ticket_creation_service.create_ticket(party.id, category.id, user.id)
