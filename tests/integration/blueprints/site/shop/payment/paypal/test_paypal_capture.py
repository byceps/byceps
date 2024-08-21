from datetime import datetime
from unittest.mock import patch

from freezegun import freeze_time
from paypalhttp import HttpError
import pytest

from byceps.events.base import EventUser
from byceps.events.shop import ShopOrderPaidEvent
from byceps.services.party.models import Party
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import order_checkout_service, order_service
from byceps.services.shop.order.models.order import Order, Orderer, OrderID
from byceps.services.shop.shop.models import Shop
from byceps.services.shop.storefront.models import Storefront
from byceps.services.site.models import Site, SiteID
from byceps.services.user.models.user import User

from tests.helpers import create_site, http_client, log_in_user
from tests.helpers.shop import (
    create_orderer,
    create_shop_snippet,
)

from .helpers import json_to_obj


@pytest.fixture(scope='module')
def shop(make_brand, make_shop, admin_user: User) -> Shop:
    brand = make_brand()
    shop = make_shop(brand.id)
    create_shop_snippet(shop.id, admin_user, 'payment_instructions', 'en', '')

    return shop


@pytest.fixture(scope='module')
def storefront(
    shop: Shop, make_order_number_sequence, make_storefront
) -> Storefront:
    order_number_sequence = make_order_number_sequence(shop.id)

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture(scope='module')
def site(party: Party, storefront: Storefront) -> Site:
    return create_site(
        SiteID('paypal-enabled-api-site'),
        party.brand_id,
        party_id=party.id,
        storefront_id=storefront.id,
    )


@pytest.fixture(scope='module')
def site_app(site: Site, make_site_app):
    server_name = f'{site.id}.acmecon.test'
    app = make_site_app(server_name, site.id)
    with app.app_context():
        yield app


@pytest.fixture(scope='module')
def orderer_user(make_user) -> User:
    return make_user()


@pytest.fixture(scope='module')
def orderer(orderer_user: User) -> Orderer:
    user = orderer_user
    log_in_user(user.id)
    return create_orderer(user)


@pytest.fixture()
def order(
    make_product, shop: Shop, storefront: Storefront, orderer: Orderer
) -> Order:
    product = make_product(storefront.shop_id)

    cart = Cart(shop.currency)
    cart.add_item(product, 1)

    order, _ = order_checkout_service.place_order(
        storefront, orderer, cart
    ).unwrap()
    return order


@patch(
    'byceps.blueprints.site.shop.payment.paypal.views._check_transaction_against_order'
)
@patch(
    'byceps.blueprints.site.shop.payment.paypal.views._extract_transaction_id'
)
@patch('byceps.blueprints.site.shop.payment.paypal.views.paypal.client.execute')
@patch('byceps.signals.shop.order_paid.send')
@patch(
    'byceps.services.shop.order.email.order_email_service.send_email_for_paid_order_to_orderer'
)
def test_payment_success(
    order_email_service_mock,
    order_paid_signal_send_mock,
    paypal_client_mock,
    extract_transaction_id_mock,
    check_transaction_mock,
    site_app,
    storefront: Storefront,
    site: Site,
    orderer_user: User,
    order: Order,
):
    assert not order.is_paid

    extract_transaction_id_mock.return_value = 'dummy-transaction-id'
    check_transaction_mock.return_value = True
    paypal_client_mock.return_value = create_response(200)

    payment_state_updated_at = datetime.utcnow()

    with freeze_time(payment_state_updated_at):
        response = call_capture_api(site_app, order)
    assert response.status_code == 200

    assert paypal_client_mock.call_count == 1
    assert check_transaction_mock.call_count == 1
    assert extract_transaction_id_mock.call_count == 1

    order_processed = get_order(order.id)
    assert order_processed.is_paid
    assert order_processed.payment_method == 'paypal'

    order_email_service_mock.assert_called_once_with(order_processed)

    event = ShopOrderPaidEvent(
        occurred_at=payment_state_updated_at,
        initiator=EventUser.from_user(orderer_user),
        order_id=order.id,
        order_number=order.order_number,
        orderer=EventUser.from_user(orderer_user),
        payment_method='paypal',
    )
    order_paid_signal_send_mock.assert_called_once_with(None, event=event)


@patch(
    'byceps.blueprints.site.shop.payment.paypal.views._check_transaction_against_order'
)
@patch('byceps.blueprints.site.shop.payment.paypal.views.paypal.client.execute')
def test_payment_manipulation_denied(
    paypal_client_mock,
    check_transaction_mock,
    site_app,
    site: Site,
    order: Order,
):
    assert not order.is_paid

    check_transaction_mock.return_value = False
    paypal_client_mock.return_value = create_response(200)

    response = call_capture_api(site_app, order)
    assert response.status_code == 400

    assert paypal_client_mock.call_count == 1
    assert check_transaction_mock.call_count == 1

    order_processed = get_order(order.id)
    assert not order_processed.is_paid


@patch('byceps.blueprints.site.shop.payment.paypal.views.paypal.client.execute')
def test_paypal_api_failure(
    paypal_client_mock, site_app, site: Site, order: Order
):
    paypal_client_mock.side_effect = HttpError('Not found', 404, None)

    response = call_capture_api(site_app, order)
    assert response.status_code == 400

    assert paypal_client_mock.call_count == 1


# helpers


def create_response(status_code: int):
    return json_to_obj(
        """
        {
            "status_code": %d,
            "result": {
                "id": "dummy-paypal-order-id"
            }
        }
        """
        % status_code
    )


def call_capture_api(app, order: Order):
    payload = {
        'paypal_order_id': 'dummy-paypal-order-id',
        'shop_order_id': order.id,
    }

    with http_client(app, user_id=order.placed_by.id) as client:
        return client.post('/shop/payment/paypal/capture', json=payload)


def get_order(order_id: OrderID) -> Order:
    return order_service.get_order(order_id)
