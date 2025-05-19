"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from decimal import Decimal

from moneyed import Money
import pytest


from byceps.config.models import AppMode
from byceps.services.shop.order.models.order import (
    Address,
    LineItem,
    LineItemID,
    LineItemProcessingState,
    Order,
    Orderer,
    OrderID,
    OrderNumber,
    OrderState,
    PaymentState,
)
from byceps.services.shop.product.models import (
    ProductID,
    ProductNumber,
    ProductType,
)
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID

from tests.helpers import generate_token, generate_uuid


@pytest.fixture(scope='package')
def app(make_app):
    tz = 'Europe/Berlin'

    app = make_app(
        AppMode.site,
        additional_config={
            'LOCALE': 'de',
            'TIMEZONE': tz,
            'BABEL_DEFAULT_TIMEZONE': tz,
        },
    )

    with app.app_context():
        yield app


@pytest.fixture(scope='package')
def build_line_item():
    def _wrapper(
        order_number: OrderNumber,
        product_number: ProductNumber,
        name: str,
        unit_price: Money,
        quantity: int,
        line_amount: Money,
    ) -> LineItem:
        return LineItem(
            id=LineItemID(generate_uuid()),
            order_number=order_number,
            product_id=ProductID(generate_uuid()),
            product_number=product_number,
            product_type=ProductType.other,
            name=name,
            unit_price=unit_price,
            tax_rate=Decimal('0.19'),
            quantity=quantity,
            line_amount=line_amount,
            processing_required=True,
            processing_result={},
            processed_at=None,
            processing_state=LineItemProcessingState.pending,
        )

    return _wrapper


@pytest.fixture(scope='package')
def build_order(orderer: Orderer):
    def _wrapper(
        created_at: datetime,
        order_number: OrderNumber,
        line_items: list[LineItem],
        total_amount: Money,
        payment_state: PaymentState,
        cancellation_reason: str | None,
        is_open: bool,
        is_canceled: bool,
        is_paid: bool,
        state: OrderState,
    ) -> Order:
        return Order(
            id=OrderID(generate_uuid()),
            created_at=created_at,
            shop_id=ShopID(generate_token()),
            storefront_id=StorefrontID(generate_token()),
            order_number=order_number,
            placed_by=orderer.user,
            company=orderer.company,
            first_name=orderer.first_name,
            last_name=orderer.last_name,
            address=Address(
                country=orderer.country,
                postal_code=orderer.postal_code,
                city=orderer.city,
                street=orderer.street,
            ),
            line_items=line_items,
            total_amount=total_amount,
            is_invoiced=False,
            payment_method=None,
            payment_state=payment_state,
            cancellation_reason=cancellation_reason,
            is_processing_required=False,
            is_processed=False,
            is_open=is_open,
            is_canceled=is_canceled,
            is_paid=is_paid,
            is_overdue=False,
            state=state,
        )

    return _wrapper


@pytest.fixture(scope='package')
def build_open_order(build_order):
    def _wrapper(
        created_at: datetime,
        order_number: OrderNumber,
        line_items: list[LineItem],
        total_amount: Money,
    ) -> Order:
        return build_order(
            created_at=created_at,
            order_number=order_number,
            line_items=line_items,
            total_amount=total_amount,
            payment_state=PaymentState.open,
            cancellation_reason=None,
            is_open=True,
            is_canceled=False,
            is_paid=False,
            state=OrderState.open,
        )

    return _wrapper


@pytest.fixture(scope='package')
def build_canceled_order(build_order):
    def _wrapper(
        created_at: datetime,
        order_number: OrderNumber,
        line_items: list[LineItem],
        total_amount: Money,
        cancellation_reason: str,
    ) -> Order:
        return build_order(
            created_at=created_at,
            order_number=order_number,
            line_items=line_items,
            total_amount=total_amount,
            payment_state=PaymentState.canceled_before_paid,
            cancellation_reason=cancellation_reason,
            is_open=False,
            is_canceled=True,
            is_paid=False,
            state=OrderState.canceled,
        )

    return _wrapper


@pytest.fixture(scope='package')
def build_paid_order(build_order):
    def _wrapper(
        created_at: datetime,
        order_number: OrderNumber,
        line_items: list[LineItem],
        total_amount: Money,
    ) -> Order:
        return build_order(
            created_at=created_at,
            order_number=order_number,
            line_items=line_items,
            total_amount=total_amount,
            payment_state=PaymentState.paid,
            cancellation_reason=None,
            is_open=False,
            is_canceled=False,
            is_paid=True,
            state=OrderState.complete,
        )

    return _wrapper
