"""
byceps.services.shop.order.email.order_email_example_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Optional

from flask_babel import gettext
from moneyed import EUR, Money

from .....config import ConfigurationError
from .....database import generate_uuid
from .....typing import BrandID, UserID

from ....email.transfer.models import Message
from ....user.models.user import User

from ...shop import shop_service
from ...shop.transfer.models import ShopID
from ...storefront.transfer.models import StorefrontID

from ..transfer.number import OrderNumber
from ..transfer.order import (
    Address,
    Order,
    OrderID,
    LineItem,
    OrderState,
    PaymentState,
)

from . import order_email_service
from .order_email_service import OrderEmailData


EXAMPLE_USER_ID = UserID(generate_uuid())


class EmailAssemblyFailed(Exception):
    pass


def build_example_placed_order_message_text(
    shop_id: ShopID, locale: str
) -> str:
    """Assemble an exemplary e-mail for a placed order."""
    shop = shop_service.get_shop(shop_id)

    order = _build_order(
        shop.id, PaymentState.open, state=OrderState.open, is_open=True
    )

    data = _build_email_data(order, shop.brand_id, locale)

    try:
        message = (
            order_email_service._assemble_email_for_incoming_order_to_orderer(
                data
            )
        )
    except Exception as e:
        raise EmailAssemblyFailed(e)

    return _render_message(message)


def build_example_paid_order_message_text(shop_id: ShopID, locale: str) -> str:
    """Assemble an exemplary e-mail for a paid order."""
    shop = shop_service.get_shop(shop_id)

    order = _build_order(
        shop.id, PaymentState.paid, state=OrderState.open, is_paid=True
    )

    data = _build_email_data(order, shop.brand_id, locale)

    try:
        message = order_email_service._assemble_email_for_paid_order_to_orderer(
            data
        )
    except Exception as e:
        raise EmailAssemblyFailed(e)

    return _render_message(message)


def build_example_canceled_order_message_text(
    shop_id: ShopID, locale: str
) -> str:
    """Assemble an exemplary e-mail for a canceled order."""
    shop = shop_service.get_shop(shop_id)

    order = _build_order(
        shop.id,
        PaymentState.canceled_before_paid,
        state=OrderState.canceled,
        is_canceled=True,
        cancelation_reason=gettext('Not paid in time.'),
    )

    data = _build_email_data(order, shop.brand_id, locale)

    try:
        message = (
            order_email_service._assemble_email_for_canceled_order_to_orderer(
                data
            )
        )
    except Exception as e:
        raise EmailAssemblyFailed(e)

    return _render_message(message)


def _build_order(
    shop_id: ShopID,
    payment_state: PaymentState,
    *,
    state: OrderState,
    is_open: bool = False,
    is_canceled: bool = False,
    is_paid: bool = False,
    cancelation_reason: Optional[str] = None,
) -> Order:
    order_id = OrderID(generate_uuid())
    storefront_id = StorefrontID('storefront-1')
    order_number = OrderNumber('AWSM-ORDR-9247')

    created_at = datetime.utcnow()
    placed_by_id = EXAMPLE_USER_ID

    first_name = 'Bella-Bernadine'
    last_name = 'Ballerwurm'
    address = Address('Germany', '22999', 'Büttenwarder', 'Deichweg 23')

    total_amount = Money('42.95', EUR)
    line_items: list[LineItem] = []
    payment_method = 'bank_transfer'

    return Order(
        id=order_id,
        created_at=created_at,
        shop_id=shop_id,
        storefront_id=storefront_id,
        order_number=order_number,
        placed_by_id=placed_by_id,
        company=None,
        first_name=first_name,
        last_name=last_name,
        address=address,
        total_amount=total_amount,
        line_items=line_items,
        payment_method=payment_method,
        payment_state=payment_state,
        state=state,
        is_open=is_open,
        is_canceled=is_canceled,
        is_paid=is_paid,
        is_invoiced=False,
        is_overdue=False,
        is_processing_required=False,
        is_processed=False,
        cancelation_reason=cancelation_reason,
    )


def _build_email_data(
    order: Order, brand_id: BrandID, locale: str
) -> OrderEmailData:
    orderer = User(
        id=EXAMPLE_USER_ID,
        screen_name='Orderer',
        suspended=False,
        deleted=False,
        locale=locale,
        avatar_url=None,
    )

    return OrderEmailData(
        order=order,
        brand_id=brand_id,
        orderer=orderer,
        orderer_email_address='orderer@example.com',
    )


def _render_message(message: Message) -> str:
    if not message.sender:
        raise ConfigurationError(
            'No e-mail sender address configured for message.'
        )

    return (
        f'From: {message.sender}\n'
        f'To: {message.recipients}\n'
        f'Subject: {message.subject}\n'
        f'\n\n{message.body}\n'
    )
