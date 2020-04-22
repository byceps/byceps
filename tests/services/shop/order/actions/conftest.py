"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.party import service as party_service
from byceps.services.shop.article import service as article_service
from byceps.services.ticketing import (
    category_service as ticket_category_service,
)

from tests.helpers import create_party

from tests.services.shop.helpers import create_article


@pytest.fixture
def party(brand):
    party = create_party(brand.id)
    yield party
    party_service.delete_party(party.id)


@pytest.fixture
def article(shop):
    article = create_article(shop.id, quantity=10)
    yield article
    article_service.delete_article(article.id)


@pytest.fixture
def ticket_category(party):
    category = ticket_category_service.create_category(party.id, 'Deluxe')
    yield category
    ticket_category_service.delete_category(category.id)
