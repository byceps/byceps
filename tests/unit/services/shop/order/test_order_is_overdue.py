"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from freezegun import freeze_time
from moneyed import EUR, Money
import pytest

from byceps.services.shop.order import order_service
from byceps.services.shop.order.dbmodels.order import DbOrder
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import PaymentState
from byceps.services.shop.shop.models import ShopID
from byceps.services.shop.storefront.models import StorefrontID
from byceps.typing import UserID


@pytest.mark.parametrize(
    ('checked_at', 'payment_state', 'expected'),
    [
        (datetime(2021, 6, 25, 11, 59, 59), PaymentState.open,                 False ),
        (datetime(2021, 6, 25, 12,  0,  0), PaymentState.open,                 True ),
        (datetime(2021, 6, 25, 12,  0,  0), PaymentState.canceled_before_paid, False),
        (datetime(2021, 6, 25, 12,  0,  0), PaymentState.paid,                 False),
        (datetime(2021, 6, 25, 12,  0,  0), PaymentState.canceled_after_paid,  False),
        (datetime(2021, 6, 25, 12,  0,  1), PaymentState.open,                 True ),
    ],
)
def test_is_overdue(
    checked_at: datetime, payment_state: PaymentState, expected: bool
):
    created_at = datetime(2021, 6, 11, 11, 59, 59)
    db_order = create_db_order(created_at, payment_state)

    with freeze_time(checked_at):
        assert order_service._is_overdue(db_order) == expected


def create_db_order(
    created_at: datetime, payment_state: PaymentState
) -> DbOrder:
    db_order = DbOrder(
        created_at=created_at,
        shop_id=ShopID('anyshop'),
        storefront_id=StorefrontID('anyshop-99'),
        order_number=OrderNumber('ORDER-31337'),
        placed_by_id=UserID(UUID('b1a18832-22d4-4df5-8077-848611633332')),
        company=None,
        first_name='n/a',
        last_name='n/a',
        country='n/a',
        zip_code='n/a',
        city='n/a',
        street='n/a',
        total_amount=Money('13.37', EUR),
        processing_required=False,
    )

    db_order.payment_state = payment_state

    return db_order
