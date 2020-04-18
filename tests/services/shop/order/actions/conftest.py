"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.brand import service as brand_service
from byceps.services.party import service as party_service
from byceps.services.ticketing import (
    category_service as ticket_category_service,
)

from tests.helpers import create_brand, create_party

from tests.services.shop.helpers import create_article


@pytest.fixture
def brand():
    brand = create_brand()
    yield brand
    brand_service.delete_brand(brand.id)


@pytest.fixture
def party(brand):
    party = create_party(brand.id)
    yield party
    party_service.delete_party(party.id)


@pytest.fixture
def article(shop):
    return create_article(shop.id, quantity=10)


@pytest.fixture
def ticket_category(party):
    category = ticket_category_service.create_category(party.id, 'Deluxe')
    yield category
    ticket_category_service.delete_category(category.id)
