"""
byceps.services.shop.order.email.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notification e-mails about shop orders

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from flask import current_app
from jinja2 import FileSystemLoader

from .....services.email import service as email_service
from .....services.email.transfer.models import Message, Sender
from .....services.shop.order import service as order_service
from .....services.shop.order.transfer.models import Order, OrderID
from .....services.shop.shop import service as shop_service
from .....services.snippet import service as snippet_service
from .....services.snippet.service import SnippetNotFound
from .....services.snippet.transfer.models import Scope
from .....services.user import service as user_service
from .....util.money import format_euro_amount
from .....util.templatefilters import utc_to_local_tz
from .....util.templating import create_sandboxed_environment, load_template

from ...shop.transfer.models import ShopID


@dataclass(frozen=True)
class OrderEmailData:
    order: Order
    email_config_id: str
    orderer_screen_name: str
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
    data: OrderEmailData
) -> Message:
    order = data.order

    subject = f'Deine Bestellung ({order.order_number}) ist eingegangen.'
    template_name = 'order_placed.txt'
    template_context = _get_template_context(data)
    template_context['payment_instructions'] = _get_payment_instructions(order)
    recipient_address = data.orderer_email_address

    return _assemble_email_to_orderer(
        subject,
        template_name,
        template_context,
        data.email_config_id,
        recipient_address,
    )


def _get_payment_instructions(order: Order) -> str:
    fragment = _get_snippet_body(order.shop_id, 'email_payment_instructions')

    template = load_template(fragment)
    return template.render(order_number=order.order_number)


def _assemble_email_for_canceled_order_to_orderer(
    data: OrderEmailData
) -> Message:
    subject = (
        f'\u274c Deine Bestellung ({data.order.order_number}) '
        f'wurde storniert.'
    )
    template_name = 'order_canceled.txt'
    template_context = _get_template_context(data)
    recipient_address = data.orderer_email_address

    return _assemble_email_to_orderer(
        subject,
        template_name,
        template_context,
        data.email_config_id,
        recipient_address,
    )


def _assemble_email_for_paid_order_to_orderer(data: OrderEmailData) -> Message:
    subject = (
        f'\u2705 Deine Bestellung ({data.order.order_number}) '
        f'ist bezahlt worden.'
    )
    template_name = 'order_paid.txt'
    template_context = _get_template_context(data)
    recipient_address = data.orderer_email_address

    return _assemble_email_to_orderer(
        subject,
        template_name,
        template_context,
        data.email_config_id,
        recipient_address,
    )


def _get_order_email_data(order_id: OrderID) -> OrderEmailData:
    """Collect data required for an order e-mail template."""
    order = order_service.find_order(order_id)

    shop = shop_service.get_shop(order.shop_id)
    orderer_id = order.placed_by_id
    screen_name = user_service.find_user(orderer_id).screen_name
    email_address = user_service.get_email_address(orderer_id)

    return OrderEmailData(
        order=order,
        email_config_id=shop.email_config_id,
        orderer_screen_name=screen_name,
        orderer_email_address=email_address,
    )


def _get_template_context(order_email_data: OrderEmailData) -> Dict[str, Any]:
    """Collect data required for an order e-mail template."""
    footer = _get_footer(order_email_data.order)

    return {
        'order': order_email_data.order,
        'orderer_screen_name': order_email_data.orderer_screen_name,
        'footer': footer,
    }


def _get_footer(order: Order) -> str:
    fragment = _get_snippet_body(order.shop_id, 'email_footer')

    template = load_template(fragment)
    return template.render()


def _assemble_email_to_orderer(
    subject: str,
    template_name: str,
    template_context: Dict[str, Any],
    email_config_id: str,
    recipient_address: str,
) -> Message:
    """Assemble an email message with the rendered template as its body."""
    sender = _get_sender_address(email_config_id)
    body = _render_template(template_name, **template_context)
    recipients = [recipient_address]

    return Message(sender, recipients, subject, body)


def _get_sender_address(email_config_id: str) -> Optional[Sender]:
    config = email_service.find_config(email_config_id)

    if not config:
        current_app.logger.warning(
            'No e-mail sender configured for ID "%s".', email_config_id
        )

    return config.sender


def _get_snippet_body(shop_id: ShopID, name: str) -> str:
    scope = Scope('shop', str(shop_id))

    version = snippet_service.find_current_version_of_snippet_with_name(
        scope, name
    )

    if not version:
        raise SnippetNotFound(scope, name)

    return version.body


def _render_template(name: str, **context: Dict[str, Any]) -> str:
    templates_path = (
        Path(current_app.root_path)
        / 'services'
        / 'shop'
        / 'order'
        / 'email'
        / 'templates'
    )

    loader = FileSystemLoader(templates_path)

    env = create_sandboxed_environment(loader=loader)
    env.filters['format_euro_amount'] = format_euro_amount
    env.filters['utc_to_local_tz'] = utc_to_local_tz

    template = env.get_template(name)

    return template.render(**context)


def _send_email(message: Message) -> None:
    email_service.enqueue_message(message)
