"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.party.models import Party
from byceps.services.shop.order.models.order import Orderer
from byceps.services.ticketing.models.ticket import TicketCategory

from tests.helpers import generate_token


@pytest.fixture()
def ticket_category(make_ticket_category, party: Party) -> TicketCategory:
    title = 'Deluxe-' + generate_token()
    return make_ticket_category(party.id, title)


@pytest.fixture(scope='module')
def orderer(make_orderer, make_user) -> Orderer:
    user = make_user()
    return make_orderer(user)
