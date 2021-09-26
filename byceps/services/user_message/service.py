"""
byceps.services.user_message.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Send an e-mail message from one user to another.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from dataclasses import dataclass
from email.utils import formataddr
from pathlib import Path
from typing import Any, Dict, Optional

from flask import current_app
from jinja2 import Environment, FileSystemLoader, Template

from ...typing import UserID
from ...util import templating

from ..email import service as email_service
from ..email.transfer.models import Message
from ..site import service as site_service
from ..site.transfer.models import SiteID
from ..user import service as user_service
from ..user.transfer.models import User


@dataclass(frozen=True)
class MessageTemplateRenderResult:
    subject: str
    body: str


def send_message(
    sender_id: UserID,
    recipient_id: UserID,
    text: str,
    sender_contact_url: str,
    site_id: SiteID,
) -> None:
    """Create a message and send it."""
    message = create_message(
        sender_id, recipient_id, text, sender_contact_url, site_id
    )

    email_service.enqueue_message(message)


def create_message(
    sender_id: UserID,
    recipient_id: UserID,
    text: str,
    sender_contact_url: str,
    site_id: SiteID,
) -> Message:
    """Assemble an email message with the rendered template as its body."""
    sender = _get_user(sender_id)
    recipient = _get_user(recipient_id)
    site = site_service.get_site(site_id)
    email_config = email_service.get_config(site.brand_id)

    template_context = {
        'sender_screen_name': sender.screen_name,
        'recipient_screen_name': recipient.screen_name,
        'text': text.strip(),
        'sender_contact_url': sender_contact_url,
        'website_server_name': site.server_name,
        'website_contact_address': email_config.contact_address,
    }

    message_template_render_result = _render_message_template(template_context)

    recipient_address = user_service.get_email_address(recipient.id)
    recipient_str = _to_name_and_address_string(
        recipient.screen_name, recipient_address
    )
    recipient_strs = [recipient_str]

    subject = message_template_render_result.subject
    body = message_template_render_result.body

    return Message(email_config.sender, recipient_strs, subject, body)


def _get_user(user_id: UserID) -> User:
    user = user_service.find_active_user(user_id)

    if user is None:
        raise ValueError(f"Unknown user ID '{user_id}' or account not active")

    return user


def _to_name_and_address_string(name: Optional[str], address: str) -> str:
    # If `name` evaluates to `False`, just the address is returned.
    return formataddr((name, address))


def _render_message_template(
    context: dict[str, Optional[str]]
) -> MessageTemplateRenderResult:
    template = _get_template('message.txt')
    module = template.make_module(context)
    subject = getattr(module, 'subject')
    body = template.render(**context)

    return MessageTemplateRenderResult(subject, body)


def _get_template(name: str) -> Template:
    env = _create_template_env()
    return env.get_template(name)


def _create_template_env() -> Environment:
    templates_path = (
        Path(current_app.root_path) / 'services' / 'user_message' / 'templates'
    )

    loader = FileSystemLoader(templates_path)

    return templating.create_sandboxed_environment(
        loader=loader, autoescape=False
    )
