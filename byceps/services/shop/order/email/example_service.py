"""
byceps.services.shop.order.email.example_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import Optional

from flask_babel import gettext

from .....config import ConfigurationError
from .....database import generate_uuid
from .....typing import BrandID

from ....email.transfer.models import Message

from ...shop import service as shop_service
from ...shop.transfer.models import ShopID

from ..email.service import OrderEmailData
from ..transfer.models import Order, OrderItem, PaymentMethod, PaymentState

from . import service as shop_order_email_service


class EmailAssemblyFailed(Exception):
    pass


def build_example_placed_order_message_text(shop_id: ShopID) -> str:
    """Assemble an exemplary e-mail for a placed order."""
    shop = shop_service.get_shop(shop_id)

    order = _build_order(shop.id, PaymentState.open, is_open=True)

    data = _build_email_data(order, shop.brand_id)

    try:
        message = shop_order_email_service._assemble_email_for_incoming_order_to_orderer(
            data
        )
    except Exception as e:
        raise EmailAssemblyFailed()

    return _render_message(message)


def build_example_paid_order_message_text(shop_id: ShopID) -> str:
    """Assemble an exemplary e-mail for a paid order."""
    shop = shop_service.get_shop(shop_id)

    order = _build_order(shop.id, PaymentState.paid, is_paid=True)

    data = _build_email_data(order, shop.brand_id)

    try:
        message = (
            shop_order_email_service._assemble_email_for_paid_order_to_orderer(
                data
            )
        )
    except Exception as e:
        raise EmailAssemblyFailed()

    return _render_message(message)


def build_example_canceled_order_message_text(shop_id: ShopID) -> str:
    """Assemble an exemplary e-mail for a canceled order."""
    shop = shop_service.get_shop(shop_id)

    order = _build_order(
        shop.id,
        PaymentState.canceled_before_paid,
        is_canceled=True,
        cancelation_reason=gettext('Not paid in time.'),
    )

    data = _build_email_data(order, shop.brand_id)

    try:
        message = shop_order_email_service._assemble_email_for_canceled_order_to_orderer(
            data
        )
    except Exception as e:
        raise EmailAssemblyFailed()

    return _render_message(message)


def _build_order(
    shop_id: ShopID,
    payment_state: PaymentState,
    *,
    is_open: bool = False,
    is_canceled: bool = False,
    is_paid: bool = False,
    cancelation_reason: Optional[str] = None,
) -> Order:
    order_id = generate_uuid()
    order_number = 'AWSM-ORDR-9247'

    created_at = datetime.utcnow()
    placed_by_id = None

    first_names = 'Bella-Bernadine'
    last_name = 'Ballerwurm'
    address = None

    total_amount = Decimal('42.95')
    items: list[OrderItem] = []
    payment_method = PaymentMethod.bank_transfer

    return Order(
        order_id,
        shop_id,
        order_number,
        created_at,
        placed_by_id,
        first_names,
        last_name,
        address,
        total_amount,
        items,
        payment_method,
        payment_state,
        is_open,
        is_canceled,
        is_paid,
        False,  # is_invoiced
        False,  # is_shipping_required
        False,  # is_shipped
        cancelation_reason,
    )


def _build_email_data(order: Order, brand_id: BrandID) -> OrderEmailData:
    return OrderEmailData(
        order=order,
        brand_id=brand_id,
        orderer_screen_name='Besteller',
        orderer_email_address='besteller@example.com',
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
