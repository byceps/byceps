"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.party.transfer.models import Party
from byceps.services.shop.order.transfer.order import Orderer
from byceps.services.ticketing.transfer.models import TicketCategory
from byceps.services.user.transfer.models import User

from tests.helpers import generate_token


@pytest.fixture
def ticket_category(make_ticket_category, party: Party) -> TicketCategory:
    title = 'Deluxe-' + generate_token()
    return make_ticket_category(party.id, title)


@pytest.fixture(scope='module')
def orderer_user(make_user) -> User:
    return make_user()


@pytest.fixture(scope='module')
def orderer(make_orderer, orderer_user: User) -> Orderer:
    return make_orderer(orderer_user.id)
