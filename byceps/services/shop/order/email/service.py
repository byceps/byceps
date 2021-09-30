"""
byceps.services.shop.order.email.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notification e-mails about shop orders

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator

from flask_babel import gettext

from .....services.email import service as email_service
from .....services.email.transfer.models import Message
from .....services.shop.order import service as order_service
from .....services.shop.order.transfer.models import Order, OrderID
from .....services.shop.shop import service as shop_service
from .....services.snippet import service as snippet_service
from .....services.snippet.service import SnippetNotFound
from .....services.snippet.transfer.models import Scope
from .....services.user import service as user_service
from .....typing import BrandID
from .....util.datetime.timezone import utc_to_local_tz
from .....util.money import format_euro_amount
from .....util.templating import load_template

from ...shop.transfer.models import ShopID


@dataclass(frozen=True)
class OrderEmailData:
    order: Order
    brand_id: BrandID
    orderer_screen_name: str
    orderer_email_address: str


def send_email_for_incoming_order_to_orderer(order_id: OrderID) -> None:
    data = _get_order_email_data(order_id)

    message = _assemble_email_for_placed_order_to_orderer(data)

    _send_email(message)


def send_email_for_canceled_order_to_orderer(order_id: OrderID) -> None:
    data = _get_order_email_data(order_id)

    message = _assemble_email_for_canceled_order_to_orderer(data)

    _send_email(message)


def send_email_for_paid_order_to_orderer(order_id: OrderID) -> None:
    data = _get_order_email_data(order_id)

    message = _assemble_email_for_paid_order_to_orderer(data)

    _send_email(message)


def _assemble_email_for_placed_order_to_orderer(
    data: OrderEmailData,
) -> Message:
    order = data.order
    order_number = order.order_number

    subject = gettext(
        'Your order (%(order_number)s) has been received.',
        order_number=order_number,
    )

    date_str = _get_order_date_str(order)
    line_items = [
        '\n'.join(
            [
                f'  Bezeichnung: {line_item.description}',
                f'  Anzahl: {line_item.quantity}',
                f'  Stückpreis: {format_euro_amount(line_item.unit_price)}',
            ]
        )
        for line_item in sorted(order.line_items, key=lambda li: li.description)
    ]
    payment_instructions = _get_payment_instructions(order)
    paragraphs = [
        f'vielen Dank für deine Bestellung mit der Nummer {order_number} am {date_str} über unsere Website.',
        'Folgende Artikel hast du bestellt:',
        *line_items,
        f'  Gesamtbetrag: {format_euro_amount(order.total_amount)}',
        payment_instructions,
    ]
    body = _assemble_body(data, paragraphs)

    recipient_address = data.orderer_email_address

    return _assemble_email_to_orderer(
        subject, body, data.brand_id, recipient_address
    )


def _get_payment_instructions(order: Order) -> str:
    fragment = _get_snippet_body(order.shop_id, 'email_payment_instructions')

    template = load_template(fragment)
    return template.render(
        order_id=order.id,
        order_number=order.order_number,
    )


def _assemble_email_for_canceled_order_to_orderer(
    data: OrderEmailData,
) -> Message:
    order = data.order
    order_number = order.order_number

    subject = '\u274c ' + gettext(
        'Your order (%(order_number)s) has been canceled.',
        order_number=order_number,
    )

    date_str = _get_order_date_str(order)
    cancelation_reason = order.cancelation_reason or ''
    paragraphs = [
        f'deine Bestellung mit der Nummer {order_number} vom {date_str} wurde von uns aus folgendem Grund storniert:',
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

    subject = '\u2705 ' + gettext(
        'Your order (%(order_number)s) has been paid.',
        order_number=order_number,
    )

    date_str = _get_order_date_str(order)
    paragraphs = [
        f'vielen Dank für deine Bestellung mit der Nummer {order_number} am {date_str} über unsere Website.',
        'Wir haben deine Zahlung erhalten und deine Bestellung als „bezahlt“ erfasst.',
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
    screen_name = user_service.get_user(orderer_id).screen_name or 'UnknownUser'
    email_address = user_service.get_email_address(orderer_id)

    return OrderEmailData(
        order=order,
        brand_id=shop.brand_id,
        orderer_screen_name=screen_name,
        orderer_email_address=email_address,
    )


def _assemble_body(data: OrderEmailData, paragraphs: list[str]) -> str:
    """Assemble the plain text part of the email."""
    orderer_screen_name = data.orderer_screen_name

    salutation = f'Hallo {orderer_screen_name},'
    footer = _get_snippet_body(data.order.shop_id, 'email_footer')

    return '\n\n'.join([salutation] + paragraphs + [footer])


def _assemble_email_to_orderer(
    subject: str,
    body: str,
    brand_id: BrandID,
    recipient_address: str,
) -> Message:
    """Assemble an email message with the rendered template as its body."""
    config = email_service.get_config(brand_id)
    sender = config.sender
    recipients = [recipient_address]

    return Message(sender, recipients, subject, body)


def _get_order_date_str(order: Order) -> str:
    return utc_to_local_tz(order.created_at).strftime('%d.%m.%Y')


def _get_snippet_body(shop_id: ShopID, name: str) -> str:
    scope = Scope('shop', str(shop_id))

    version = snippet_service.find_current_version_of_snippet_with_name(
        scope, name
    )

    if not version:
        raise SnippetNotFound(scope, name)

    return version.body.strip()


def _send_email(message: Message) -> None:
    email_service.enqueue_message(message)
