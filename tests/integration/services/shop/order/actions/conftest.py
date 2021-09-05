"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.article import service as article_service

from tests.helpers import generate_token
from tests.integration.services.shop.helpers import (
    create_article,
    create_orderer,
)


@pytest.fixture
def article(shop):
    article = create_article(shop.id, total_quantity=10)
    article_id = article.id
    yield article
    article_service.delete_article(article_id)


@pytest.fixture
def ticket_category(make_ticket_category, party):
    title = 'Deluxe-' + generate_token()
    return make_ticket_category(party.id, title)


@pytest.fixture(scope='module')
def orderer_user(make_user):
    return make_user()


@pytest.fixture(scope='module')
def orderer(orderer_user):
    return create_orderer(orderer_user.id)
