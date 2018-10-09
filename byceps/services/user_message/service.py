"""
byceps.services.user_message.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Send an e-mail message from one user to another.

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import os.path
from typing import Any, Dict, Optional

from attr import attrib, attrs
from flask import current_app
from jinja2 import Environment, FileSystemLoader, Template

from ...typing import BrandID, UserID
from ...util import templating

from ..brand import service as brand_service, \
    settings_service as brand_settings_service
from ..brand.transfer.models import Brand
from ..email import service as email_service
from ..email.transfer.models import Message
from ..user.models.user import User as DbUser
from ..user import service as user_service


@attrs(frozen=True, slots=True)
class MessageTemplateRenderResult:
    subject = attrib(type=str)
    body = attrib(type=str)


def send_message(sender_id: UserID, recipient_id: UserID, text: str,
                 sender_contact_url: str, brand_id: BrandID) -> None:
    """Create a message and send it."""
    message = create_message(sender_id, recipient_id, text, sender_contact_url,
                             brand_id)

    email_service.enqueue_message(message)


def create_message(sender_id: UserID, recipient_id: UserID, text: str,
                   sender_contact_url: str, brand_id: BrandID) -> Message:
    """Create a message."""
    sender = _get_user(sender_id)
    recipient = _get_user(recipient_id)
    brand = _get_brand(brand_id)

    return _assemble_message(sender, recipient, text, sender_contact_url, brand)


def _get_user(user_id: UserID) -> DbUser:
    user = user_service.find_active_user(user_id)

    if user is None:
        raise ValueError(
            "Unknown user ID '{}' or account not active".format(user_id))

    return user


def _get_brand(brand_id: BrandID) -> Brand:
    brand = brand_service.find_brand(brand_id)

    if brand is None:
        raise ValueError("Unknown brand ID '{}'".format(brand_id))

    return brand


def _assemble_message(sender: DbUser, recipient: DbUser, text: str,
                      sender_contact_url: str, brand: Brand
                     ) -> Message:
    """Assemble an email message with the rendered template as its body."""
    brand_contact_address = brand_settings_service \
        .find_setting_value(brand.id, 'contact_email_address')

    message_template_render_result = _render_message_template(
        sender, recipient, text, sender_contact_url, brand,
        brand_contact_address)

    sender_address = email_service.get_sender_address_for_brand(brand.id)
    recipients = [recipient.email_address]
    subject = message_template_render_result.subject
    body = message_template_render_result.body

    return Message(sender_address, recipients, subject, body)


def _render_message_template(sender: DbUser, recipient: DbUser, text: str,
                             sender_contact_url: str, brand: Brand,
                             brand_contact_address: Optional[str]
                            ) -> MessageTemplateRenderResult:
    template = _get_template('message.txt')

    context = {
        'sender_screen_name': sender.screen_name,
        'recipient_screen_name': recipient.screen_name,
        'text': text.strip(),
        'sender_contact_url': sender_contact_url,
        'brand_title': brand.title,
        'brand_contact_address': brand_contact_address,
    }

    module = template.make_module(context)
    subject = getattr(module, 'subject')
    body = template.render(**context)

    return MessageTemplateRenderResult(subject, body)


def _get_template(name: str) -> Template:
    env = _create_template_env()
    return env.get_template(name)


def _create_template_env() -> Environment:
    templates_path = os.path.join(current_app.root_path,
                                  'services/user_message/templates')

    loader = FileSystemLoader(templates_path)

    return templating.create_sandboxed_environment(loader=loader,
                                                   autoescape=False)
