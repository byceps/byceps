"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from flask import Flask
from flask_babel import Babel
from moneyed import Money
import pytest


from byceps.services.shop.article.models import (
    ArticleID,
    ArticleNumber,
    ArticleType,
)
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
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID
from byceps.services.user.models.user import User
from byceps.typing import UserID

from tests.helpers import generate_token, generate_uuid


@pytest.fixture(scope='package')
def app():
    app = Flask('byceps')

    tz = 'Europe/Berlin'

    app.config.update(
        {
            'LOCALE': 'de',
            'TIMEZONE': tz,
            'BABEL_DEFAULT_TIMEZONE': tz,
        }
    )

    Babel(app)

    with app.app_context():
        yield app


@pytest.fixture(scope='package')
def orderer():
    user = User(
        id=UserID(generate_uuid()),
        screen_name=generate_token(),
        suspended=False,
        deleted=False,
        locale=None,
        avatar_url=None,
    )

    return Orderer(
        user=user,
        company=None,
        first_name='John',
        last_name='Wick',
        country='Germany',
        zip_code='22999',
        city='Büttenwarder',
        street='Deichweg 1',
    )


@pytest.fixture(scope='package')
def build_line_item():
    def _wrapper(
        order_number: OrderNumber,
        article_number: ArticleNumber,
        description: str,
        unit_price: Money,
        quantity: int,
        line_amount: Money,
    ) -> LineItem:
        return LineItem(
            id=LineItemID(generate_uuid()),
            order_number=order_number,
            article_id=ArticleID(generate_uuid()),
            article_number=article_number,
            article_type=ArticleType.other,
            description=description,
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
        cancelation_reason: str | None,
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
            placed_by_id=orderer.user.id,
            company=orderer.company,
            first_name=orderer.first_name,
            last_name=orderer.last_name,
            address=Address(
                country=orderer.country,
                zip_code=orderer.zip_code,
                city=orderer.city,
                street=orderer.street,
            ),
            line_items=line_items,
            total_amount=total_amount,
            is_invoiced=False,
            payment_method=None,
            payment_state=payment_state,
            cancelation_reason=cancelation_reason,
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
            cancelation_reason=None,
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
        cancelation_reason: str,
    ) -> Order:
        return build_order(
            created_at=created_at,
            order_number=order_number,
            line_items=line_items,
            total_amount=total_amount,
            payment_state=PaymentState.canceled_before_paid,
            cancelation_reason=cancelation_reason,
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
            cancelation_reason=None,
            is_open=False,
            is_canceled=False,
            is_paid=True,
            state=OrderState.complete,
        )

    return _wrapper
