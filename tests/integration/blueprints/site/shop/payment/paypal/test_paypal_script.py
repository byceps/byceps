from datetime import datetime
from decimal import Decimal
from string import Template

from moneyed import EUR, Money
import pytest

from byceps.services.party.models import Party
from byceps.services.shop.cart.models import Cart
from byceps.services.shop.order import order_checkout_service
from byceps.services.shop.payment import payment_gateway_service
from byceps.services.shop.payment.models import PaymentGateway
from byceps.services.shop.shop.models import Shop, ShopID
from byceps.services.shop.storefront.models import Storefront
from byceps.services.site.models import Site, SiteID
from byceps.services.snippet import snippet_service

from tests.helpers import (
    create_site,
    http_client,
    log_in_user,
)
from tests.helpers.shop import (
    create_product as _create_product,
    create_orderer,
    create_shop_snippet,
)


PAYPAL_CLIENT_ID = 'dummy-paypal-client-id'


@pytest.fixture(scope='module')
def shop(make_brand, make_shop, admin_user):
    brand = make_brand(title='NorthCon 2020')
    shop = make_shop(brand)
    snippet_id = create_shop_snippet(
        shop.id, admin_user, 'payment_instructions', 'de', ''
    )

    yield shop

    snippet_service.delete_snippet(snippet_id)


@pytest.fixture(scope='module')
def storefront(
    shop: Shop, make_order_number_sequence, make_storefront
) -> Storefront:
    order_number_sequence = make_order_number_sequence(
        shop.id, prefix='PP-99-B'
    )

    return make_storefront(shop.id, order_number_sequence.id)


@pytest.fixture(scope='module')
def payment_gateway(make_payment_gateway, storefront: Storefront) -> None:
    payment_gateway = make_payment_gateway(payment_gateway_id='paypal')
    payment_gateway_service.enable_payment_gateway_for_storefront(
        payment_gateway.id, storefront.id
    )


@pytest.fixture(scope='module')
def site(party: Party, storefront: Storefront) -> Site:
    return create_site(
        SiteID('paypal-enabled-site'),
        party.brand_id,
        party_id=party.id,
        storefront_id=storefront.id,
    )


@pytest.fixture(scope='module')
def site_app(site, make_site_app):
    server_name = f'{site.id}.acmecon.test'
    app = make_site_app(server_name, site.id)
    with app.app_context():
        yield app


@pytest.fixture(scope='module')
def app(site_app):
    site_app.config['PAYPAL_CLIENT_ID'] = PAYPAL_CLIENT_ID
    yield site_app


@pytest.fixture(scope='module')
def orderer(make_user):
    user = make_user()
    log_in_user(user.id)
    orderer = create_orderer(user)

    yield orderer


@pytest.fixture()
def cart(shop: Shop) -> Cart:
    tax_rate = Decimal('0.19')

    product1 = create_product(
        shop.id,
        'PP-A01',
        'Sample Product 1',
        Decimal('10.00'),
        tax_rate,
    )
    product2 = create_product(
        shop.id,
        'PP-A02',
        'Sample Product 2',
        Decimal('1.99'),
        tax_rate,
    )

    cart = Cart(shop.currency)
    cart.add_item(product1, 1)
    cart.add_item(product2, 3)

    return cart


@pytest.fixture()
def order(
    site: Site,
    storefront: Storefront,
    orderer,
    cart: Cart,
    payment_gateway: PaymentGateway,
):
    created_at = datetime(2015, 2, 26, 12, 26, 24)

    order, _ = order_checkout_service.place_order(
        storefront, orderer, cart, created_at=created_at
    ).unwrap()

    return order


def test_render_paypal_script(request, app, order):
    url = f'/shop/orders/{order.id!s}'

    with http_client(app, user_id=order.placed_by.id) as client:
        response = client.get(url)

    filename = request.fspath.dirpath('paypal_script.html')
    template_source = filename.read_text('utf-8')
    expected_script_content_template = Template(template_source)

    expected_script_content = expected_script_content_template.substitute(
        client_id=PAYPAL_CLIENT_ID, order_id=order.id
    )

    body = response.get_data(as_text=True)

    assert expected_script_content in body


# helpers


def create_product(
    shop_id: ShopID,
    item_number,
    name: str,
    price: Decimal,
    tax_rate: Decimal,
):
    return _create_product(
        shop_id,
        item_number=item_number,
        name=name,
        price=Money(price, EUR),
        tax_rate=tax_rate,
        total_quantity=10,
    )
