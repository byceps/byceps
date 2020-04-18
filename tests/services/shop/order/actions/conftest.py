"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.ticketing import (
    category_service as ticket_category_service,
)

from tests.helpers import create_brand, create_party

from tests.services.shop.helpers import create_article


@pytest.fixture
def brand():
    return create_brand()


@pytest.fixture
def party(brand):
    return create_party(brand.id)


@pytest.fixture
def article(shop):
    return create_article(shop.id, quantity=10)


@pytest.fixture
def ticket_category(party):
    category = ticket_category_service.create_category(party.id, 'Deluxe')
    yield category
    ticket_category_service.delete_category(category.id)
