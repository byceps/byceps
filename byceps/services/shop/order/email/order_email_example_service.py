"""
byceps.services.shop.order.email.order_email_example_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from flask_babel import gettext
from moneyed import EUR, Money

from byceps.config.errors import ConfigurationError
from byceps.services.brand.models import Brand
from byceps.services.email.models import Message, NameAndAddress
from byceps.services.shop.order.models.number import OrderNumber
from byceps.services.shop.order.models.order import (
    Address,
    LineItem,
    Order,
    OrderID,
    OrderState,
    PaymentState,
)
from byceps.services.shop.shop.models import Shop
from byceps.services.shop.storefront.models import StorefrontID
from byceps.services.snippet.errors import SnippetNotFoundError
from byceps.services.user.models.user import User, UserID
from byceps.util.result import Err, Ok, Result
from byceps.util.uuid import generate_uuid4

from . import order_email_service
from .order_email_service import OrderEmailData


def build_example_placed_order_message_text(
    shop: Shop, sender: NameAndAddress, brand: Brand, locale: str
) -> Result[str, str]:
    """Assemble an exemplary e-mail for a placed order."""
    order = _build_order(
        shop, PaymentState.open, state=OrderState.open, is_open=True
    )

    data = _build_email_data(sender, order, brand)

    try:
        message_result = (
            order_email_service.assemble_email_for_incoming_order_to_orderer(
                data, locale
            )
        )
    except Exception as e:
        return Err(str(e))

    if message_result.is_err():
        return _snippet_not_found_error_to_text(message_result.unwrap_err())

    return Ok(_render_message(message_result.unwrap()))


def build_example_paid_order_message_text(
    shop: Shop, sender: NameAndAddress, brand: Brand, locale: str
) -> Result[str, str]:
    """Assemble an exemplary e-mail for a paid order."""
    order = _build_order(
        shop, PaymentState.paid, state=OrderState.open, is_paid=True
    )

    data = _build_email_data(sender, order, brand)

    try:
        message_result = (
            order_email_service.assemble_email_for_paid_order_to_orderer(
                data, locale
            )
        )
    except Exception as e:
        return Err(str(e))

    if message_result.is_err():
        return _snippet_not_found_error_to_text(message_result.unwrap_err())

    return Ok(_render_message(message_result.unwrap()))


def build_example_canceled_order_message_text(
    shop: Shop, sender: NameAndAddress, brand: Brand, locale: str
) -> Result[str, str]:
    """Assemble an exemplary e-mail for a canceled order."""
    order = _build_order(
        shop,
        PaymentState.canceled_before_paid,
        state=OrderState.canceled,
        is_canceled=True,
        cancellation_reason=gettext('Not paid in time.'),
    )

    data = _build_email_data(sender, order, brand)

    try:
        message_result = (
            order_email_service.assemble_email_for_canceled_order_to_orderer(
                data, locale
            )
        )
    except Exception as e:
        return Err(str(e))

    if message_result.is_err():
        return _snippet_not_found_error_to_text(message_result.unwrap_err())

    return Ok(_render_message(message_result.unwrap()))


def _build_order(
    shop: Shop,
    payment_state: PaymentState,
    *,
    state: OrderState,
    is_open: bool = False,
    is_canceled: bool = False,
    is_paid: bool = False,
    cancellation_reason: str | None = None,
) -> Order:
    order_id = OrderID(generate_uuid4())
    storefront_id = StorefrontID('storefront-1')
    order_number = OrderNumber('AWSM-ORDR-9247')

    created_at = datetime.utcnow()

    placed_by = User(
        id=UserID(generate_uuid4()),
        screen_name='Orderer',
        initialized=True,
        suspended=False,
        deleted=False,
        locale=None,
        avatar_url=None,
    )

    first_name = 'Bella-Bernadine'
    last_name = 'Ballerwurm'
    address = Address(
        country='Germany',
        postal_code='22999',
        city='Büttenwarder',
        street='Deichweg 23',
    )

    total_amount = Money('42.95', EUR)
    line_items: list[LineItem] = []
    payment_method = 'bank_transfer'

    return Order(
        id=order_id,
        created_at=created_at,
        shop_id=shop.id,
        storefront_id=storefront_id,
        order_number=order_number,
        placed_by=placed_by,
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
        cancellation_reason=cancellation_reason,
    )


def _build_email_data(
    sender: NameAndAddress, order: Order, brand: Brand
) -> OrderEmailData:
    return OrderEmailData(
        sender=sender,
        order=order,
        brand=brand,
        orderer=order.placed_by,
        orderer_email_address='orderer@example.com',
    )


def _render_message(message: Message) -> str:
    if not message.sender:
        raise ConfigurationError(
            'No e-mail sender address configured for message.'
        )

    return (
        f'From: {message.sender.format()}\n'
        f'To: {message.recipients}\n'
        f'Subject: {message.subject}\n'
        f'\n\n{message.body}\n'
    )


def _snippet_not_found_error_to_text(error: SnippetNotFoundError) -> Err[str]:
    return Err(
        f'Snippet "{error.name}" not found '
        f'for language code "{error.language_code}" '
        f'in scope "{error.scope.type_}/{error.scope.name}"'
    )
