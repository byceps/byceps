"""
byceps.services.shop.order.email.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notification e-mails about shop orders

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import os.path
from typing import Any, Dict, Optional

from attr import attrib, attrs
from flask import current_app
from jinja2 import FileSystemLoader

from .....services.brand import service as brand_service
from .....services.brand.transfer.models import Brand
from .....services.email import service as email_service
from .....services.email.transfer.models import Message
from .....services.party import service as party_service
from .....services.party.transfer.models import Party
from .....services.shop.order import service as order_service
from .....services.shop.order.transfer.models import Order, OrderID
from .....services.shop.shop import service as shop_service
from .....services.user.models.user import User
from .....typing import BrandID
from .....util.money import format_euro_amount
from .....util.templating import create_sandboxed_environment


@attrs(frozen=True, slots=True)
class OrderEmailData:
    order = attrib(type=Order)
    party = attrib(type=Party)
    brand = attrib(type=Brand)
    placed_by = attrib(type=User)


def send_email_for_incoming_order_to_orderer(order_id: OrderID) -> None:
    message = _assemble_email_for_incoming_order_to_orderer(order_id)

    _send_email(message)


def send_email_for_canceled_order_to_orderer(order_id: OrderID) -> None:
    message = _assemble_email_for_canceled_order_to_orderer(order_id)

    _send_email(message)


def send_email_for_paid_order_to_orderer(order_id: OrderID) -> None:
    message = _assemble_email_for_paid_order_to_orderer(order_id)

    _send_email(message)


def _assemble_email_for_incoming_order_to_orderer(order_id: OrderID) -> Message:
    data = _get_order_email_data(order_id)

    subject = 'Deine Bestellung ({}) ist eingegangen.' \
        .format(data.order.order_number)
    template_name = 'order_placed.txt'
    template_context = _get_template_context(data)
    recipient_address = data.placed_by.email_address

    return _assemble_email_to_orderer(subject, template_name, template_context,
                                      data.party, recipient_address)


def _assemble_email_for_canceled_order_to_orderer(order_id: OrderID) -> Message:
    data = _get_order_email_data(order_id)

    subject = 'Deine Bestellung ({}) wurde storniert.' \
        .format(data.order.order_number)
    template_name = 'order_canceled.txt'
    template_context = _get_template_context(data)
    recipient_address = data.placed_by.email_address

    return _assemble_email_to_orderer(subject, template_name, template_context,
                                      data.party, recipient_address)


def _assemble_email_for_paid_order_to_orderer(order_id: OrderID) -> Message:
    data = _get_order_email_data(order_id)

    subject = 'Deine Bestellung ({}) ist bezahlt worden.' \
        .format(data.order.order_number)
    template_name = 'order_paid.txt'
    template_context = _get_template_context(data)
    recipient_address = data.placed_by.email_address

    return _assemble_email_to_orderer(subject, template_name, template_context,
                                      data.party, recipient_address)


def _get_order_email_data(order_id: OrderID) -> OrderEmailData:
    """Collect data required for an order e-mail template."""
    order_entity = order_service.find_order(order_id)

    order = order_entity.to_transfer_object()
    shop = shop_service.get_shop(order.shop_id)
    party = party_service.find_party(shop.party_id)
    brand = brand_service.find_brand(party.brand_id)
    placed_by = order_entity.placed_by

    return OrderEmailData(
        order=order,
        party=party,
        brand=brand,
        placed_by=placed_by,
    )


def _get_template_context(order_email_data: OrderEmailData) -> Dict[str, Any]:
    """Collect data required for an order e-mail template."""
    return {
        'order': order_email_data.order,
        'party': order_email_data.party,
        'brand': order_email_data.brand,
        'placed_by': order_email_data.placed_by,
    }


def _assemble_email_to_orderer(subject: str, template_name: str,
                               template_context: Dict[str, Any], party: Party,
                               recipient_address: str) -> Message:
    """Assemble an email message with the rendered template as its body."""
    sender_address = _get_sender_address_for_brand(party.brand_id)

    template_context['contact_email_address'] = sender_address

    body = _render_template(template_name, **template_context)
    sender = sender_address
    recipients = [recipient_address]

    return Message(sender, recipients, subject, body)


def _get_sender_address_for_brand(brand_id: BrandID) -> Optional[str]:
    sender_address = email_service.find_sender_address_for_brand(brand_id)

    if not sender_address:
        current_app.logger.warning(
            'No e-mail sender address configured for brand ID "%s".', brand_id)

    return sender_address


def _render_template(name: str, **context: Dict[str, Any]) -> str:
    templates_path = os.path.join(
        current_app.root_path,
        'services/shop/order/email/templates')

    loader = FileSystemLoader(templates_path)

    env = create_sandboxed_environment(loader=loader)
    env.filters['format_euro_amount'] = format_euro_amount

    template = env.get_template(name)

    return template.render(**context)


def _send_email(message: Message) -> None:
    email_service.enqueue_message(message)
