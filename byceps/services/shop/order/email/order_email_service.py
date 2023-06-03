"""
byceps.services.shop.order.email.order_email_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notification e-mails about shop orders

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass

from flask_babel import format_date, gettext

from byceps.services.email import (
    email_config_service,
    email_footer_service,
    email_service,
)
from byceps.services.email.models import Message
from byceps.services.shop.order import order_payment_service, order_service
from byceps.services.shop.order.models.order import Order, OrderID
from byceps.services.shop.shop import shop_service
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.typing import BrandID
from byceps.util.l10n import force_user_locale, format_money, get_user_locale


@dataclass(frozen=True)
class OrderEmailData:
    order: Order
    brand_id: BrandID
    orderer: User
    orderer_email_address: str
    language_code: str


@dataclass(frozen=True)
class OrderEmailText:
    subject: str
    body_main_part: str


def send_email_for_incoming_order_to_orderer(order_id: OrderID) -> None:
    data = _get_order_email_data(order_id)

    message = assemble_email_for_incoming_order_to_orderer(data)

    _send_email(message)


def send_email_for_canceled_order_to_orderer(order_id: OrderID) -> None:
    data = _get_order_email_data(order_id)

    message = assemble_email_for_canceled_order_to_orderer(data)

    _send_email(message)


def send_email_for_paid_order_to_orderer(order_id: OrderID) -> None:
    data = _get_order_email_data(order_id)

    message = assemble_email_for_paid_order_to_orderer(data)

    _send_email(message)


def assemble_email_for_incoming_order_to_orderer(
    data: OrderEmailData,
) -> Message:
    payment_instructions = order_payment_service.get_email_payment_instructions(
        data.order, data.language_code
    )

    footer = _get_footer(data)

    text = assemble_text_for_incoming_order_to_orderer(
        data.order, data.orderer, payment_instructions
    )

    return _assemble_email_to_orderer(data, text, footer)


def assemble_text_for_incoming_order_to_orderer(
    order: Order, orderer: User, payment_instructions: str
) -> OrderEmailText:
    with force_user_locale(orderer):
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
            for line_item in sorted(
                order.line_items, key=lambda li: li.description
            )
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
) -> Message:
    footer = _get_footer(data)

    text = assemble_text_for_canceled_order_to_orderer(data.order, data.orderer)

    return _assemble_email_to_orderer(data, text, footer)


def assemble_text_for_canceled_order_to_orderer(
    order: Order, orderer: User
) -> OrderEmailText:
    with force_user_locale(orderer):
        subject = '\u274c ' + gettext(
            'Your order (%(order_number)s) has been canceled.',
            order_number=order.order_number,
        )

        date_str = format_date(order.created_at)
        cancelation_reason = order.cancelation_reason or ''
        paragraphs = [
            gettext(
                'your order %(order_number)s on %(order_date)s has been canceled by us for this reason:',
                order_number=order.order_number,
                order_date=date_str,
            ),
            cancelation_reason,
        ]
        body_main_part = '\n\n'.join(paragraphs)

    return OrderEmailText(subject=subject, body_main_part=body_main_part)


def assemble_email_for_paid_order_to_orderer(data: OrderEmailData) -> Message:
    footer = _get_footer(data)

    text = assemble_text_for_paid_order_to_orderer(data.order, data.orderer)

    return _assemble_email_to_orderer(data, text, footer)


def assemble_text_for_paid_order_to_orderer(
    order: Order, orderer: User
) -> OrderEmailText:
    with force_user_locale(orderer):
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


def _get_order_email_data(order_id: OrderID) -> OrderEmailData:
    """Collect data required for an order e-mail template."""
    order = order_service.get_order(order_id)

    shop = shop_service.get_shop(order.shop_id)
    orderer_id = order.placed_by_id
    orderer = user_service.get_user(orderer_id)
    email_address = user_service.get_email_address(orderer_id)
    language_code = get_user_locale(orderer)

    return OrderEmailData(
        order=order,
        brand_id=shop.brand_id,
        orderer=orderer,
        orderer_email_address=email_address,
        language_code=language_code,
    )


def _get_footer(data: OrderEmailData) -> str:
    """Obtain the brand's email footer."""
    return email_footer_service.get_footer(data.brand_id, data.language_code)


def _assemble_body(data: OrderEmailData, main_part: str, footer: str) -> str:
    """Assemble the plain text part of the email."""
    screen_name = data.orderer.screen_name or 'UnknownUser'
    with force_user_locale(data.orderer):
        salutation = gettext('Hello %(screen_name)s,', screen_name=screen_name)

    parts = [salutation, main_part, footer]
    return '\n\n'.join(parts)


def _assemble_email_to_orderer(
    data: OrderEmailData, text: OrderEmailText, footer: str
) -> Message:
    """Assemble an email message with the rendered template as its body."""
    config = email_config_service.get_config(data.brand_id)
    sender = config.sender
    recipients = [data.orderer_email_address]

    body = _assemble_body(data, text.body_main_part, footer)

    return Message(sender, recipients, text.subject, body)


def _send_email(message: Message) -> None:
    email_service.enqueue_message(message)
