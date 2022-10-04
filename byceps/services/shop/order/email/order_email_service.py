"""
byceps.services.shop.order.email.order_email_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notification e-mails about shop orders

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass

from flask_babel import format_currency, format_date, gettext

from .....services.email import (
    config_service as email_config_service,
    service as email_service,
)
from .....services.email.transfer.models import Message
from .....services.shop.order import order_service
from .....services.shop.order.transfer.order import Order, OrderID
from .....services.shop.shop import shop_service
from .....services.snippet import service as snippet_service
from .....services.snippet.service import SnippetNotFound
from .....services.snippet.transfer.models import Scope
from .....services.user import user_service
from .....services.user.transfer.models import User
from .....typing import BrandID
from .....util.l10n import force_user_locale
from .....util.templating import load_template


@dataclass(frozen=True)
class OrderEmailData:
    order: Order
    brand_id: BrandID
    orderer: User
    orderer_email_address: str


def send_email_for_incoming_order_to_orderer(order_id: OrderID) -> None:
    data = _get_order_email_data(order_id)

    message = _assemble_email_for_incoming_order_to_orderer(data)

    _send_email(message)


def send_email_for_canceled_order_to_orderer(order_id: OrderID) -> None:
    data = _get_order_email_data(order_id)

    message = _assemble_email_for_canceled_order_to_orderer(data)

    _send_email(message)


def send_email_for_paid_order_to_orderer(order_id: OrderID) -> None:
    data = _get_order_email_data(order_id)

    message = _assemble_email_for_paid_order_to_orderer(data)

    _send_email(message)


def _assemble_email_for_incoming_order_to_orderer(
    data: OrderEmailData,
) -> Message:
    order = data.order
    order_number = order.order_number

    with force_user_locale(data.orderer):
        subject = gettext(
            'Your order (%(order_number)s) has been received.',
            order_number=order_number,
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
                    + format_currency(line_item.unit_price, 'EUR'),
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
            + format_currency(order.total_amount, 'EUR')
        )
        payment_instructions = _get_payment_instructions(order)
        paragraphs = [
            gettext(
                'thank you for your order %(order_number)s on %(order_date)s through our website.',
                order_number=order_number,
                order_date=date_str,
            ),
            gettext('You have ordered these items:'),
            *line_items,
            total_amount,
            payment_instructions,
        ]
        body = _assemble_body(data, paragraphs)

    recipient_address = data.orderer_email_address

    return _assemble_email_to_orderer(
        subject, body, data.brand_id, recipient_address
    )


def _get_payment_instructions(order: Order) -> str:
    scope = Scope('shop', str(order.shop_id))
    snippet_content = _get_snippet_body(scope, 'email_payment_instructions')

    template = load_template(snippet_content)
    return template.render(
        order_id=order.id,
        order_number=order.order_number,
    )


def _assemble_email_for_canceled_order_to_orderer(
    data: OrderEmailData,
) -> Message:
    order = data.order
    order_number = order.order_number

    with force_user_locale(data.orderer):
        subject = '\u274c ' + gettext(
            'Your order (%(order_number)s) has been canceled.',
            order_number=order_number,
        )

        date_str = format_date(order.created_at)
        cancelation_reason = order.cancelation_reason or ''
        paragraphs = [
            gettext(
                'your order %(order_number)s on %(order_date)s has been canceled by us for this reason:',
                order_number=order_number,
                order_date=date_str,
            ),
            cancelation_reason,
        ]
        body = _assemble_body(data, paragraphs)

    recipient_address = data.orderer_email_address

    return _assemble_email_to_orderer(
        subject, body, data.brand_id, recipient_address
    )


def _assemble_email_for_paid_order_to_orderer(data: OrderEmailData) -> Message:
    order = data.order
    order_number = order.order_number

    with force_user_locale(data.orderer):
        subject = '\u2705 ' + gettext(
            'Your order (%(order_number)s) has been paid.',
            order_number=order_number,
        )

        date_str = format_date(order.created_at)
        paragraphs = [
            gettext(
                'thank you for your order %(order_number)s on %(order_date)s through our website.',
                order_number=order_number,
                order_date=date_str,
            ),
            gettext(
                'We have received your payment and have marked your order as paid.'
            ),
        ]
        body = _assemble_body(data, paragraphs)

    recipient_address = data.orderer_email_address

    return _assemble_email_to_orderer(
        subject, body, data.brand_id, recipient_address
    )


def _get_order_email_data(order_id: OrderID) -> OrderEmailData:
    """Collect data required for an order e-mail template."""
    order = order_service.get_order(order_id)

    shop = shop_service.get_shop(order.shop_id)
    orderer_id = order.placed_by_id
    orderer = user_service.get_user(orderer_id)
    email_address = user_service.get_email_address(orderer_id)

    return OrderEmailData(
        order=order,
        brand_id=shop.brand_id,
        orderer=orderer,
        orderer_email_address=email_address,
    )


def _assemble_body(data: OrderEmailData, paragraphs: list[str]) -> str:
    """Assemble the plain text part of the email."""
    screen_name = data.orderer.screen_name or 'UnknownUser'
    salutation = gettext('Hello %(screen_name)s,', screen_name=screen_name)

    scope = Scope.for_brand(data.brand_id)
    footer = _get_snippet_body(scope, 'email_footer')

    return '\n\n'.join([salutation] + paragraphs + [footer])


def _assemble_email_to_orderer(
    subject: str,
    body: str,
    brand_id: BrandID,
    recipient_address: str,
) -> Message:
    """Assemble an email message with the rendered template as its body."""
    config = email_config_service.get_config(brand_id)
    sender = config.sender
    recipients = [recipient_address]

    return Message(sender, recipients, subject, body)


def _get_snippet_body(scope: Scope, name: str) -> str:
    version = snippet_service.find_current_version_of_snippet_with_name(
        scope, name
    )

    if not version:
        raise SnippetNotFound(scope, name)

    return version.body.strip()


def _send_email(message: Message) -> None:
    email_service.enqueue_message(message)
