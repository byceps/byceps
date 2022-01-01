"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from decimal import Decimal
from unittest.mock import patch

import pytest

from byceps.events.shop import ShopOrderPlaced
from byceps.services.shop.article import service as article_service
from byceps.services.shop.article.transfer.models import (
    Article,
    ArticleID,
    ArticleNumber,
)
from byceps.services.shop.order import service as order_service
from byceps.services.shop.shop.transfer.models import Shop, ShopID
from byceps.services.shop.storefront.transfer.models import Storefront
from byceps.services.site import service as site_service
from byceps.services.site.transfer.models import Site, SiteID
from byceps.services.snippet import service as snippet_service

from tests.helpers import create_site, generate_token, http_client, log_in_user
from tests.integration.services.shop.helpers import (
    create_article,
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


@pytest.fixture(scope='module')
def shop(make_brand, make_shop, admin_user) -> Shop:
    brand = make_brand()
    shop = make_shop(brand.id)
    snippet_id = create_shop_fragment(
        shop.id, admin_user.id, 'payment_instructions', 'Send all ur moneyz!'
    )

    yield shop

    snippet_service.delete_snippet(snippet_id)


@pytest.fixture(scope='module')
def storefront(
    shop: Shop, make_order_number_sequence, make_storefront
) -> Storefront:
    order_number_sequence = make_order_number_sequence(
        shop.id, prefix='ORDR-23-B', value=4
    )

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture(scope='module')
def site(make_brand, storefront: Storefront) -> Site:
    brand = make_brand()
    site = create_site(
        SiteID('acmecon-2014-shop-website'),
        brand.id,
        storefront_id=storefront.id,
    )
    yield site
    site_service.delete_site(site.id)


@pytest.fixture(scope='module')
def site_app(site: Site, make_site_app):
    app = make_site_app(site.id)
    with app.app_context():
        yield app


@pytest.fixture
def article(admin_app, shop: Shop) -> Article:
    return create_article(shop.id, total_quantity=5)


@pytest.fixture(scope='module')
def orderer(admin_app, user):
    log_in_user(user.id)
    return user


@patch('byceps.signals.shop.order_placed.send')
@patch('byceps.blueprints.site.shop.order.views.order_email_service')
def test_order(
    order_email_service_mock,
    order_placed_mock,
    site_app,
    site: Site,
    admin_user,
    orderer,
    article: Article,
):
    assert get_article_quantity(article.id) == 5

    url = '/shop/order'
    article_quantity_key = f'article_{article.id}'
    form_data = {
        **COMMON_FORM_DATA,
        article_quantity_key: 3,
    }
    with http_client(site_app, user_id=orderer.id) as client:
        response = client.post(url, data=form_data)

    assert get_article_quantity(article.id) == 2

    order = get_single_order_by(orderer.id)
    assert_order(order, 'ORDR-23-B00005', 1)

    first_line_item = order.line_items[0]
    assert_line_item(
        first_line_item,
        article.item_number,
        article.price,
        article.tax_rate,
        3,
    )

    order_email_service_mock.send_email_for_incoming_order_to_orderer.assert_called_once_with(
        order.id
    )

    event = ShopOrderPlaced(
        occurred_at=order.created_at,
        initiator_id=orderer.id,
        initiator_screen_name=orderer.screen_name,
        order_id=order.id,
        order_number=order.order_number,
        orderer_id=orderer.id,
        orderer_screen_name=orderer.screen_name,
    )
    order_placed_mock.assert_called_once_with(None, event=event)

    order_detail_page_url = f'http://www.acmecon.test/shop/orders/{order.id}'

    assert_response_headers(response, order_detail_page_url)

    with http_client(site_app, user_id=orderer.id) as client:
        assert_order_detail_page_works(
            client, order_detail_page_url, order.order_number
        )

    order_service.delete_order(order.id)


@patch('byceps.signals.shop.order_placed.send')
@patch('byceps.blueprints.site.shop.order.views.order_email_service')
def test_order_single(
    order_email_service_mock,
    order_placed_mock,
    site_app,
    site: Site,
    admin_user,
    orderer,
    article: Article,
):
    assert get_article_quantity(article.id) == 5

    url = f'/shop/order_single/{article.id!s}'
    form_data = {
        **COMMON_FORM_DATA,
        'quantity': 1,  # TODO: Test with `3` if limitation is removed.
    }
    with http_client(site_app, user_id=orderer.id) as client:
        response = client.post(url, data=form_data)

    assert get_article_quantity(article.id) == 4

    order = get_single_order_by(orderer.id)
    assert_order(order, 'ORDR-23-B00006', 1)

    first_line_item = order.line_items[0]
    assert_line_item(
        first_line_item,
        article.item_number,
        article.price,
        article.tax_rate,
        1,
    )

    order_email_service_mock.send_email_for_incoming_order_to_orderer.assert_called_once_with(
        order.id
    )

    event = ShopOrderPlaced(
        occurred_at=order.created_at,
        initiator_id=orderer.id,
        initiator_screen_name=orderer.screen_name,
        order_id=order.id,
        order_number=order.order_number,
        orderer_id=orderer.id,
        orderer_screen_name=orderer.screen_name,
    )
    order_placed_mock.assert_called_once_with(None, event=event)

    order_detail_page_url = f'http://www.acmecon.test/shop/orders/{order.id}'

    assert_response_headers(response, order_detail_page_url)

    with http_client(site_app, user_id=orderer.id) as client:
        assert_order_detail_page_works(
            client, order_detail_page_url, order.order_number
        )

    order_service.delete_order(order.id)


# helpers


def get_article_quantity(article_id: ArticleID) -> int:
    article = article_service.get_article(article_id)
    return article.quantity


def get_single_order_by(user_id):
    orders = order_service.get_orders_placed_by_user(user_id)
    assert len(orders) == 1
    return orders[0]


def assert_response_headers(response, order_detail_page_url: str) -> None:
    assert response.status_code == 302
    assert response.headers.get('Location') == order_detail_page_url


def assert_order(order, order_number, line_item_quantity: int) -> None:
    assert order.order_number == order_number
    assert len(order.line_items) == line_item_quantity


def assert_line_item(
    line_item,
    article_item_number: ArticleNumber,
    unit_price: Decimal,
    tax_rate: Decimal,
    quantity: int,
) -> None:
    assert line_item.article_number == article_item_number
    assert line_item.unit_price == unit_price
    assert line_item.tax_rate == tax_rate
    assert line_item.quantity == quantity


def assert_order_detail_page_works(client, order_detail_page_url, order_number):
    response = client.get(order_detail_page_url)
    assert response.status_code == 200
    assert order_number in response.get_data(as_text=True)
