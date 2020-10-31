"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.shop.article import service as article_service
from byceps.services.ticketing import (
    category_service as ticket_category_service,
)

from testfixtures.shop_order import create_orderer

from tests.integration.services.shop.helpers import create_article


@pytest.fixture
def article(shop):
    article = create_article(shop.id, total_quantity=10)
    article_id = article.id
    yield article
    article_service.delete_article(article_id)


@pytest.fixture
def ticket_category(party):
    category = ticket_category_service.create_category(party.id, 'Deluxe')
    yield category
    ticket_category_service.delete_category(category.id)


@pytest.fixture(scope='package')
def orderer_user(make_user_with_detail):
    return make_user_with_detail('TicketsOrderer')


@pytest.fixture(scope='package')
def orderer(orderer_user):
    return create_orderer(orderer_user)
