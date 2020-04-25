"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch

import pytest

from byceps.events.shop import ShopOrderPlaced
from byceps.services.shop.article import service as article_service
from byceps.services.shop.order.models.order import Order
from byceps.services.shop.order import service as order_service
from byceps.services.shop.sequence import service as sequence_service
from byceps.services.shop.shop import service as shop_service
from byceps.services.shop.storefront import service as storefront_service
from byceps.services.site import service as site_service
from byceps.services.snippet import service as snippet_service

from tests.helpers import create_site, http_client, login_user
from tests.integration.services.shop.helpers import (
    create_article,
    create_shop,
    create_shop_fragment,
)


COMMON_FORM_DATA = {
    'first_names': 'Hiro',
    'last_name': 'Protagonist',
    'country': 'State of Mind',
    'zip_code': '31337',
    'city': 'Atrocity',
    'street': 'L33t Street 101',
}


@pytest.fixture
def shop(email_config, admin_user):
    shop = create_shop('shop-1')
    snippet_id = create_shop_fragment(
        shop.id, admin_user.id, 'payment_instructions', 'Send all ur moneyz!'
    )

    yield shop

    snippet_service.delete_snippet(snippet_id)
    shop_service.delete_shop(shop.id)


@pytest.fixture
def order_number_sequence_id(shop) -> None:
    sequence_id = sequence_service.create_order_number_sequence(
        shop.id, 'AEC-01-B', value=4
    )

    yield sequence_id

    sequence_service.delete_order_number_sequence(sequence_id)


@pytest.fixture
def storefront(shop, order_number_sequence_id) -> None:
    storefront = storefront_service.create_storefront(
        f'{shop.id}-storefront', shop.id, order_number_sequence_id, closed=False
    )

    yield storefront

    storefront_service.delete_storefront(storefront.id)


@pytest.fixture
def site(storefront):
    site = create_site('acmecon-2014-website', storefront_id=storefront.id)
    yield site
    site_service.delete_site(site.id)


@pytest.fixture
def article(admin_app, shop):
    article = create_article(shop.id, quantity=5)
    article_id = article.id
    yield article
    article_service.delete_article(article_id)


@pytest.fixture
def orderer(admin_app, user):
    login_user(user.id)
    return user


@patch('byceps.blueprints.shop.order.signals.order_placed.send')
@patch('byceps.blueprints.shop.order.views.order_email_service')
def test_order(
    order_email_service_mock,
    order_placed_mock,
    party_app,
    site,
    admin_user,
    orderer,
    article,
):
    assert get_article_quantity(article.id) == 5

    url = '/shop/order'
    article_quantity_key = f'article_{article.id}'
    form_data = {
        **COMMON_FORM_DATA,
        article_quantity_key: 3,
    }
    with http_client(party_app, user_id=orderer.id) as client:
        response = client.post(url, data=form_data)

    assert get_article_quantity(article.id) == 2

    order = Order.query.filter_by(placed_by_id=orderer.id).one()
    assert_order(order, 'AEC-01-B00005', 1)

    first_order_item = order.items[0]
    assert_order_item(
        first_order_item,
        article.id,
        article.price,
        article.tax_rate,
        3,
    )

    order_email_service_mock.send_email_for_incoming_order_to_orderer.assert_called_once_with(
        order.id
    )

    event = ShopOrderPlaced(
        occurred_at=order.created_at,
        order_id=order.id,
        initiator_id=order.placed_by_id,
    )
    order_placed_mock.assert_called_once_with(None, event=event)

    order_detail_page_url = f'http://www.acmecon.test/shop/orders/{order.id}'

    assert_response_headers(response, order_detail_page_url)

    with http_client(party_app, user_id=orderer.id) as client:
        assert_order_detail_page_works(
            client, order_detail_page_url, order.order_number
        )

    order_service.delete_order(order.id)


@patch('byceps.blueprints.shop.order.signals.order_placed.send')
@patch('byceps.blueprints.shop.order.views.order_email_service')
def test_order_single(
    order_email_service_mock,
    order_placed_mock,
    party_app,
    site,
    admin_user,
    orderer,
    article,
):
    assert get_article_quantity(article.id) == 5

    url = f'/shop/order_single/{article.id!s}'
    form_data = {
        **COMMON_FORM_DATA,
        'quantity': 1,  # TODO: Test with `3` if limitation is removed.
    }
    with http_client(party_app, user_id=orderer.id) as client:
        response = client.post(url, data=form_data)

    assert get_article_quantity(article.id) == 4

    order = Order.query.filter_by(placed_by_id=orderer.id).one()
    assert_order(order, 'AEC-01-B00005', 1)

    first_order_item = order.items[0]
    assert_order_item(
        first_order_item,
        article.id,
        article.price,
        article.tax_rate,
        1,
    )

    order_email_service_mock.send_email_for_incoming_order_to_orderer.assert_called_once_with(
        order.id
    )

    event = ShopOrderPlaced(
        occurred_at=order.created_at,
        order_id=order.id,
        initiator_id=order.placed_by_id,
    )
    order_placed_mock.assert_called_once_with(None, event=event)

    order_detail_page_url = f'http://www.acmecon.test/shop/orders/{order.id}'

    assert_response_headers(response, order_detail_page_url)

    with http_client(party_app, user_id=orderer.id) as client:
        assert_order_detail_page_works(
            client, order_detail_page_url, order.order_number
        )

    order_service.delete_order(order.id)


# helpers


def get_article_quantity(article_id):
    article = article_service.get_article(article_id)
    return article.quantity


def assert_response_headers(response, order_detail_page_url):
    assert response.status_code == 302
    assert response.headers.get('Location') == order_detail_page_url


def assert_order(order, order_number, item_quantity):
    assert order.order_number == order_number
    assert len(order.items) == item_quantity


def assert_order_item(order_item, article_id, unit_price, tax_rate, quantity):
    assert order_item.article.id == article_id
    assert order_item.unit_price == unit_price
    assert order_item.tax_rate == tax_rate
    assert order_item.quantity == quantity


def assert_order_detail_page_works(client, order_detail_page_url, order_number):
    response = client.get(order_detail_page_url)
    assert response.status_code == 200
    assert 'AEC-01-B00005' in response.get_data(as_text=True)
