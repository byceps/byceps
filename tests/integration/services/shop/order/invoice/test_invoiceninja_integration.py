"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.shop.invoice import invoiceninja_service
from byceps.services.shop.invoice.errors import (
    InvoiceDeniedForFreeOrderError,
    InvoiceProviderNotConfiguredError,
)
from byceps.services.shop.invoice.models import DownloadableInvoice
from byceps.services.shop.order import order_command_service, order_service
from byceps.services.shop.order.models.detailed_order import AdminDetailedOrder
from byceps.services.user.models.user import User
from byceps.util.result import Err, Ok

from tests.helpers import generate_token
from tests.helpers.shop import place_order


@pytest.fixture()
def invoiceninja_config(admin_app):
    admin_app.config['INVOICENINJA_BASE_URL'] = 'https://invoiceninja.example'
    admin_app.config['INVOICENINJA_API_KEY'] = '12345'

    yield

    admin_app.config.pop('INVOICENINJA_BASE_URL', None)
    admin_app.config.pop('INVOICENINJA_API_KEY', None)


@pytest.fixture(scope='module')
def orderer(make_user, make_orderer):
    user = make_user()
    return make_orderer(user)


@pytest.fixture()
def placed_order(
    make_product, admin_app, shop, storefront, orderer
) -> AdminDetailedOrder:
    product = make_product(storefront.shop_id)
    products_with_quantity = [(product, 1)]
    order = place_order(shop, storefront, orderer, products_with_quantity)

    return get_admin_detailed_order(order.id)


@pytest.fixture()
def make_paid_order(placed_order: AdminDetailedOrder):
    """Provide a paid order."""

    def _wrapper(payment_method: str, initiator: User) -> AdminDetailedOrder:
        paid_order, _ = order_command_service.mark_order_as_paid(
            placed_order.id, payment_method, initiator
        ).unwrap()

        return get_admin_detailed_order(paid_order.id)

    return _wrapper


def test_get_invoice_for_order_not_configured(
    placed_order: AdminDetailedOrder, admin_user: User
):
    # No Invoice Ninja configuration.

    initiator = admin_user

    actual = invoiceninja_service.get_downloadable_invoice_for_order(
        placed_order, draft=True, initiator=initiator
    )

    assert actual == Err(InvoiceProviderNotConfiguredError())


def test_get_invoice_for_free_order(
    invoiceninja_config,
    make_paid_order,
    admin_user: User,
):
    initiator = admin_user

    payment_method = 'free'
    paid_order = make_paid_order(payment_method, initiator)

    actual = invoiceninja_service.get_downloadable_invoice_for_order(
        paid_order, draft=True, initiator=initiator
    )

    assert actual == Err(InvoiceDeniedForFreeOrderError())


def test_get_existing_invoice_for_order(
    respx_mock,
    invoiceninja_config,
    make_paid_order,
    admin_user: User,
):
    initiator = admin_user

    payment_method = 'bank_transfer'
    paid_order = make_paid_order(payment_method, initiator)

    invitation_key = 'D2J234DFA'

    respx_mock.get(
        f'https://invoiceninja.example/api/v1/invoices?is_deleted=false&filter={paid_order.order_number}'
    ).respond(
        json={
            'data': [
                {
                    'id': '4openg4a7A',
                    'invitations': [
                        {
                            'key': invitation_key,
                        },
                    ],
                    'paid_to_date': 0,
                    'client_id': 'WpmbkZXazJ',
                    'number': generate_token(),
                },
            ],
        },
    )

    respx_mock.get(
        f'https://invoiceninja.example/api/v1/invoice/{invitation_key}/download'
    ).respond(
        headers={
            'Content-Disposition': 'attachment; filename=TEST-123.pdf',
            'Content-Type': 'application/pdf',
        },
        content=b'%PDF',
    )

    actual = invoiceninja_service.get_downloadable_invoice_for_order(
        paid_order, draft=True, initiator=initiator
    )

    assert actual == Ok(
        DownloadableInvoice(
            content_disposition='attachment; filename=TEST-123.pdf',
            content_type='application/pdf',
            content=b'%PDF',
        )
    )


def get_admin_detailed_order(order_id) -> AdminDetailedOrder:
    detailed_order = order_service.find_order_with_details_for_admin(order_id)

    if not detailed_order:
        raise Exception(
            f'Could not find detailed order for order ID: {order_id}'
        )

    return detailed_order
