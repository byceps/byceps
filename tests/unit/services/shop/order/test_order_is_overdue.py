"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from freezegun import freeze_time
import pytest

from byceps.services.shop.order.dbmodels.order import Order as DbOrder
from byceps.services.shop.order.service import _is_overdue as is_overdue
from byceps.services.shop.order.transfer.number import OrderNumber
from byceps.services.shop.order.transfer.order import PaymentState
from byceps.services.shop.shop.transfer.models import ShopID
from byceps.services.shop.storefront.transfer.models import StorefrontID
from byceps.typing import UserID


@pytest.mark.parametrize(
    'created_at, payment_state, expected',
    [
        (datetime(2021, 6, 12, 12, 0, 0), PaymentState.open,                 True),
        (datetime(2021, 6, 12, 12, 0, 0), PaymentState.canceled_before_paid, True),
        (datetime(2021, 6, 12, 12, 0, 0), PaymentState.paid,                 True),
        (datetime(2021, 6, 12, 12, 0, 0), PaymentState.canceled_after_paid,  True),
        (datetime(2021, 6, 13, 20, 0, 0), PaymentState.open,                 False),
        (datetime(2021, 6, 13, 20, 0, 1), PaymentState.open,                 False),
        (datetime(2021, 6, 14, 12, 0, 0), PaymentState.open,                 False),
        (datetime(2021, 6, 14, 12, 0, 0), PaymentState.canceled_before_paid, False),
        (datetime(2021, 6, 14, 12, 0, 0), PaymentState.paid,                 False),
        (datetime(2021, 6, 14, 12, 0, 0), PaymentState.canceled_after_paid,  False),
    ],
)
def test_is_overdue(
    created_at: datetime, payment_state: PaymentState, expected: bool
):
    db_order = create_db_order(created_at)

    with freeze_time(datetime(2021, 6, 27, 20, 0, 0)) as now:
        assert is_overdue(db_order) == expected


def create_db_order(created_at: datetime) -> DbOrder:
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
    )

    db_order.payment_state = PaymentState.open

    return db_order
