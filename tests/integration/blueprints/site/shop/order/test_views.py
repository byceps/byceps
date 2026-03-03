"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from decimal import Decimal
from unittest.mock import patch

from moneyed import Money
import pytest

from byceps.byceps_app import BycepsApp
from byceps.services.shop.order import order_service
from byceps.services.shop.order.events import ShopOrderPlacedEvent
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import LineItem, Order
from byceps.services.shop.product import product_service
from byceps.services.shop.product.models import (
    Product,
    ProductID,
    ProductNumber,
)
from byceps.services.shop.shop.models import Shop
from byceps.services.shop.storefront.models import Storefront
from byceps.services.site.models import Site, SiteID
from byceps.services.user.models import User, UserID

from tests.helpers import create_site, http_client, log_in_user
from tests.helpers.shop import create_shop_snippet


SERVER_NAME = 'site-for-orders.acmecon.test'

BASE_URL = f'http://{SERVER_NAME}'

COMMON_FORM_DATA: dict[str, str] = {
    'first_name': 'Hiro',
    'last_name': 'Protagonist',
    'country': 'State of Mind',
    'postal_code': '31337',
    'city': 'Atrocity',
    'street': 'L33t Street 101',
}


@pytest.fixture(scope='module')
def shop(make_brand, make_shop, admin_user: User):
    brand = make_brand()
    shop = make_shop(brand)
    create_shop_snippet(
        shop.id,
        admin_user,
        'payment_instructions',
        'de',
        'Send all ur moneyz!',
    )

    return shop


@pytest.fixture(scope='module')
def storefront(
    shop: Shop, make_order_number_sequence, make_storefront
) -> Storefront:
    order_number_sequence = make_order_number_sequence(
        shop.id, prefix='ORDR-23-B', value=4
    )

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture(scope='module')
def site(make_brand, storefront: Storefront):
    brand = make_brand()
    return create_site(
        SiteID('acmecon-2014-shop-website'),
        brand.id,
        storefront_id=storefront.id,
    )


@pytest.fixture(scope='module')
def site_app(site: Site, make_site_app):
    app = make_site_app(SERVER_NAME, site.id)
    with app.app_context():
        yield app


@pytest.fixture()
def product(make_product, admin_app: BycepsApp, shop: Shop) -> Product:
    return make_product(shop.id, total_quantity=5)


@patch('byceps.services.shop.order.signals.order_placed.send')
@patch('byceps.services.shop.order.blueprints.site.service.order_email_service')
def test_order(
    order_email_service_mock,
    order_placed_mock,
    site_app: BycepsApp,
    site: Site,
    admin_user: User,
    make_user,
    product: Product,
):
    assert get_product_quantity(product.id) == 5

    orderer_user = make_user()
    log_in_user(orderer_user.id)

    url = f'{BASE_URL}/shop/order'
    product_quantity_key = f'product_{product.id}'
    form_data: dict[str, int | str] = {
        **COMMON_FORM_DATA,
        'company': 'ACME Corp.',
        product_quantity_key: 3,
    }
    with http_client(site_app, user_id=orderer_user.id) as client:
        response = client.post(url, data=form_data)

    assert get_product_quantity(product.id) == 2

    order = get_single_order_by(orderer_user.id)
    assert_order(order, OrderNumber('ORDR-23-B00005'), 1)

    first_line_item = order.line_items[0]
    assert_line_item(
        first_line_item,
        product.id,
        product.item_number,
        product.price,
        product.tax_rate,
        3,
    )

    order_email_service_mock.send_email_for_incoming_order_to_orderer.assert_called_once_with(
        order
    )

    event = ShopOrderPlacedEvent(
        occurred_at=order.created_at,
        initiator=orderer_user,
        order_id=order.id,
        order_number=order.order_number,
        orderer=orderer_user,
    )
    order_placed_mock.assert_called_once_with(None, event=event)

    order_detail_page_url = f'/shop/orders/{order.id}'

    assert_response_headers(response, order_detail_page_url)

    with http_client(site_app, user_id=orderer_user.id) as client:
        assert_order_detail_page_works(
            client, BASE_URL + order_detail_page_url, order.order_number
        )


@patch('byceps.services.shop.order.signals.order_placed.send')
@patch('byceps.services.shop.order.blueprints.site.service.order_email_service')
def test_order_single(
    order_email_service_mock,
    order_placed_mock,
    site_app: BycepsApp,
    site: Site,
    admin_user: User,
    make_user,
    product: Product,
):
    assert get_product_quantity(product.id) == 5

    orderer_user = make_user()
    log_in_user(orderer_user.id)

    url = f'{BASE_URL}/shop/order_single/{product.id!s}'
    form_data: dict[str, int | str] = {
        **COMMON_FORM_DATA,
        'quantity': 1,  # Overridden with fixed quantity 1 anyway.
    }
    with http_client(site_app, user_id=orderer_user.id) as client:
        response = client.post(url, data=form_data)

    assert get_product_quantity(product.id) == 4

    order = get_single_order_by(orderer_user.id)
    assert_order(order, OrderNumber('ORDR-23-B00006'), 1)

    first_line_item = order.line_items[0]
    assert_line_item(
        first_line_item,
        product.id,
        product.item_number,
        product.price,
        product.tax_rate,
        1,
    )

    order_email_service_mock.send_email_for_incoming_order_to_orderer.assert_called_once_with(
        order
    )

    event = ShopOrderPlacedEvent(
        occurred_at=order.created_at,
        initiator=orderer_user,
        order_id=order.id,
        order_number=order.order_number,
        orderer=orderer_user,
    )
    order_placed_mock.assert_called_once_with(None, event=event)

    order_detail_page_url = f'/shop/orders/{order.id}'

    assert_response_headers(response, order_detail_page_url)

    with http_client(site_app, user_id=orderer_user.id) as client:
        assert_order_detail_page_works(
            client, BASE_URL + order_detail_page_url, order.order_number
        )


# helpers


def get_product_quantity(product_id: ProductID) -> int:
    product = product_service.get_product(product_id)
    return product.quantity


def get_single_order_by(user_id: UserID) -> Order:
    orders = order_service.get_orders_placed_by_user(user_id)
    assert len(orders) == 1
    return orders[0]


def assert_response_headers(response, order_detail_page_url: str) -> None:
    assert response.status_code == 302
    assert response.location == order_detail_page_url


def assert_order(
    order: Order, order_number: OrderNumber, line_item_quantity: int
) -> None:
    assert order.order_number == order_number
    assert len(order.line_items) == line_item_quantity


def assert_line_item(
    line_item: LineItem,
    product_id: ProductID,
    product_number: ProductNumber,
    unit_price: Money,
    tax_rate: Decimal,
    quantity: int,
) -> None:
    assert line_item.product_id == product_id
    assert line_item.product_number == product_number
    assert line_item.unit_price == unit_price
    assert line_item.tax_rate == tax_rate
    assert line_item.quantity == quantity


def assert_order_detail_page_works(
    client, order_detail_page_url: str, order_number: OrderNumber
):
    response = client.get(order_detail_page_url)
    assert response.status_code == 200
    assert str(order_number) in response.get_data(as_text=True)
