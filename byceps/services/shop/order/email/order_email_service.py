"""
byceps.services.shop.order.email.order_email_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notification e-mails about shop orders

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial

from flask_babel import force_locale, format_date, gettext
import structlog

from byceps.services.brand import brand_service
from byceps.services.brand.models import Brand
from byceps.services.email import (
    email_config_service,
    email_footer_service,
    email_service,
)
from byceps.services.email.models import Message, NameAndAddress
from byceps.services.shop.order import order_payment_service
from byceps.services.shop.order.models.order import Order
from byceps.services.shop.shop import shop_service
from byceps.services.snippet.errors import SnippetNotFoundError
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.util.l10n import format_money, get_user_locale
from byceps.util.result import Err, Ok, Result


log = structlog.get_logger()


@dataclass(frozen=True)
class OrderEmailData:
    sender: NameAndAddress
    order: Order
    brand: Brand
    orderer: User
    orderer_email_address: str


@dataclass(frozen=True)
class OrderEmailText:
    subject: str
    body_main_part: str


def send_email_for_incoming_order_to_orderer(order: Order) -> None:
    data = _get_order_email_data(order)
    language_code = get_user_locale(data.orderer)

    message_result = assemble_email_for_incoming_order_to_orderer(
        data, language_code
    )
    if message_result.is_err():
        log.error(
            'Assembling email for incoming order to orderer failed',
            error=message_result.unwrap_err(),
        )
        return

    _send_email(message_result.unwrap())


def send_email_for_canceled_order_to_orderer(order: Order) -> None:
    data = _get_order_email_data(order)
    language_code = get_user_locale(data.orderer)

    message_result = assemble_email_for_canceled_order_to_orderer(
        data, language_code
    )
    if message_result.is_err():
        log.error(
            'Assembling email for canceled order to orderer failed',
            error=message_result.unwrap_err(),
        )
        return

    _send_email(message_result.unwrap())


def send_email_for_paid_order_to_orderer(order: Order) -> None:
    data = _get_order_email_data(order)
    language_code = get_user_locale(data.orderer)

    message_result = assemble_email_for_paid_order_to_orderer(
        data, language_code
    )
    if message_result.is_err():
        log.error(
            'Assembling email for paid order to orderer failed',
            error=message_result.unwrap_err(),
        )
        return

    _send_email(message_result.unwrap())


def assemble_email_for_incoming_order_to_orderer(
    data: OrderEmailData,
    language_code: str,
) -> Result[Message, SnippetNotFoundError]:
    footer_result = email_footer_service.get_footer(data.brand, language_code)
    if footer_result.is_err():
        return Err(footer_result.unwrap_err())

    footer = footer_result.unwrap()

    payment_instructions_result = (
        order_payment_service.get_email_payment_instructions(
            data.order, language_code
        )
    )
    if payment_instructions_result.is_err():
        return Err(payment_instructions_result.unwrap_err())

    payment_instructions = payment_instructions_result.unwrap()

    assemble_text_for_incoming_order_to_orderer_with_payment_instructions = (
        partial(
            assemble_text_for_incoming_order_to_orderer,
            payment_instructions=payment_instructions,
        )
    )

    assembled = _assemble_email(
        data,
        language_code,
        footer,
        assemble_text_for_incoming_order_to_orderer_with_payment_instructions,
    )
    return Ok(assembled)


def assemble_text_for_incoming_order_to_orderer(
    order: Order, payment_instructions: str
) -> OrderEmailText:
    subject = gettext(
        'Your order (%(order_number)s) has been received.',
        order_number=order.order_number,
    )

    date_str = format_date(order.created_at)
    indentation = '  '
    line_items = [
        '\n'.join(
            [
                indentation
                + gettext('Description')
                + ': '
                + line_item.description,
                indentation
                + gettext('Quantity')
                + ': '
                + str(line_item.quantity),
                indentation
                + gettext('Unit price')
                + ': '
                + format_money(line_item.unit_price),
                indentation
                + gettext('Line price')
                + ': '
                + format_money(line_item.line_amount),
            ]
        )
        for line_item in sorted(order.line_items, key=lambda li: li.description)
    ]
    total_amount = (
        indentation
        + gettext('Total amount')
        + ': '
        + format_money(order.total_amount)
    )
    paragraphs = [
        gettext(
            'thank you for your order %(order_number)s on %(order_date)s through our website.',
            order_number=order.order_number,
            order_date=date_str,
        ),
        gettext('You have ordered these items:'),
        *line_items,
        total_amount,
        payment_instructions,
    ]
    body_main_part = '\n\n'.join(paragraphs)

    return OrderEmailText(subject=subject, body_main_part=body_main_part)


def assemble_email_for_canceled_order_to_orderer(
    data: OrderEmailData,
    language_code: str,
) -> Result[Message, SnippetNotFoundError]:
    footer_result = email_footer_service.get_footer(data.brand, language_code)
    if footer_result.is_err():
        return Err(footer_result.unwrap_err())

    footer = footer_result.unwrap()

    assembled = _assemble_email(
        data, language_code, footer, assemble_text_for_canceled_order_to_orderer
    )
    return Ok(assembled)


def assemble_text_for_canceled_order_to_orderer(order: Order) -> OrderEmailText:
    subject = '\u274c ' + gettext(
        'Your order (%(order_number)s) has been canceled.',
        order_number=order.order_number,
    )

    date_str = format_date(order.created_at)
    cancellation_reason = order.cancellation_reason or ''
    paragraphs = [
        gettext(
            'your order %(order_number)s on %(order_date)s has been canceled by us for this reason:',
            order_number=order.order_number,
            order_date=date_str,
        ),
        cancellation_reason,
    ]
    body_main_part = '\n\n'.join(paragraphs)

    return OrderEmailText(subject=subject, body_main_part=body_main_part)


def assemble_email_for_paid_order_to_orderer(
    data: OrderEmailData, language_code: str
) -> Result[Message, SnippetNotFoundError]:
    footer_result = email_footer_service.get_footer(data.brand, language_code)
    if footer_result.is_err():
        return Err(footer_result.unwrap_err())

    footer = footer_result.unwrap()

    assembled = _assemble_email(
        data, language_code, footer, assemble_text_for_paid_order_to_orderer
    )
    return Ok(assembled)


def assemble_text_for_paid_order_to_orderer(order: Order) -> OrderEmailText:
    subject = '\u2705 ' + gettext(
        'Your order (%(order_number)s) has been paid.',
        order_number=order.order_number,
    )

    date_str = format_date(order.created_at)
    paragraphs = [
        gettext(
            'thank you for your order %(order_number)s on %(order_date)s through our website.',
            order_number=order.order_number,
            order_date=date_str,
        ),
        gettext(
            'We have received your payment and have marked your order as paid.'
        ),
    ]
    body_main_part = '\n\n'.join(paragraphs)

    return OrderEmailText(subject=subject, body_main_part=body_main_part)


def _get_order_email_data(order: Order) -> OrderEmailData:
    """Collect data required for an order e-mail template."""
    shop = shop_service.get_shop(order.shop_id)
    brand = brand_service.get_brand(shop.brand_id)
    email_config = email_config_service.get_config(brand.id)
    orderer = order.placed_by
    email_address = user_service.get_email_address(orderer.id)

    return OrderEmailData(
        sender=email_config.sender,
        order=order,
        brand=brand,
        orderer=orderer,
        orderer_email_address=email_address,
    )


def _assemble_email(
    data: OrderEmailData,
    language_code: str,
    footer: str,
    func: Callable[[Order], OrderEmailText],
) -> Message:
    with force_locale(language_code):
        text = func(data.order)
        body = _assemble_body_parts(data.orderer, text.body_main_part, footer)

    return Message(
        sender=data.sender,
        recipients=[data.orderer_email_address],
        subject=text.subject,
        body=body,
    )


def _assemble_body_parts(recipient: User, main_part: str, footer: str) -> str:
    """Assemble the plain text body part of the email."""
    screen_name = recipient.screen_name or 'UnknownUser'
    salutation = gettext('Hello %(screen_name)s,', screen_name=screen_name)

    parts = [salutation, main_part, footer]
    return '\n\n'.join(parts)


def _send_email(message: Message) -> None:
    email_service.enqueue_message(message)
