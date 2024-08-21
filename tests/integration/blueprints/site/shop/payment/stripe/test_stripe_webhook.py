"""
:Copyright: 2020 Micha Ober
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from freezegun import freeze_time
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


@pytest.fixture(scope='module')
def shop(make_brand, make_shop, admin_user: User) -> Shop:
    brand = make_brand()
    shop = make_shop(brand.id)
    create_shop_snippet(shop.id, admin_user, 'payment_instructions', 'de', '')

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
        SiteID('stripe-enabled-site'),
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
    'byceps.blueprints.site.shop.payment.stripe.views._check_transaction_against_order'
)
@patch('stripe.Webhook.construct_event')
@patch('byceps.signals.shop.order_paid.send')
@patch(
    'byceps.services.shop.order.email.order_email_service.send_email_for_paid_order_to_orderer'
)
def test_stripe_webhook_payment_intent_succeeded(
    order_email_service_mock,
    order_paid_signal_send_mock,
    stripe_webhook_construct_mock,
    check_transaction_mock,
    site_app,
    orderer_user: User,
    order: Order,
):
    assert not order.is_paid

    check_transaction_mock.return_value = True
    webhook_event = create_event('checkout.session.completed', order.id)
    stripe_webhook_construct_mock.return_value = webhook_event

    payment_state_updated_at = datetime.utcnow()

    with freeze_time(payment_state_updated_at):
        response = call_webhook(site_app)
    assert response.status_code == 200

    assert stripe_webhook_construct_mock.call_count == 1
    check_transaction_mock.assert_called_once_with(
        webhook_event.data.object, order
    )

    order_processed = get_order(order.id)
    assert order_processed.is_paid
    assert order_processed.payment_method == 'stripe'

    order_email_service_mock.assert_called_once_with(order_processed)

    event = ShopOrderPaidEvent(
        occurred_at=payment_state_updated_at,
        initiator=EventUser.from_user(orderer_user),
        order_id=order.id,
        order_number=order.order_number,
        orderer=EventUser.from_user(orderer_user),
        payment_method='stripe',
    )
    order_paid_signal_send_mock.assert_called_once_with(None, event=event)


@patch('stripe.Webhook.construct_event')
def test_stripe_webhook_unknown_event(
    stripe_webhook_construct_mock,
    site_app,
):
    stripe_webhook_construct_mock.return_value = create_event(
        'invalid.event', ''
    )

    response = call_webhook(site_app)
    assert response.status_code == 400

    assert stripe_webhook_construct_mock.call_count == 1


# helpers


def create_event(event_type: str, order_id: OrderID):
    return SimpleNamespace(
        type=event_type,
        data=SimpleNamespace(
            object=SimpleNamespace(
                id='dummy-payment-id',
                metadata={
                    'shop_order_id': order_id,
                },
                payment_intent='dummy-payment-intent',
            ),
        ),
    )


def call_webhook(app):
    with http_client(app) as client:
        return client.post('/shop/payment/stripe/webhook')


def get_order(order_id: OrderID) -> Order:
    return order_service.get_order(order_id)
