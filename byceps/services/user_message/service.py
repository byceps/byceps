"""
byceps.services.user_message.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Send an e-mail message from one user to another.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from email.utils import formataddr
from typing import Optional

from flask import current_app

from ...typing import UserID
from ...util import templating

from ..email import service as email_service
from ..email.transfer.models import Message
from ..site import service as site_service
from ..site.transfer.models import SiteID
from ..user import service as user_service
from ..user.transfer.models import User


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

    sender_screen_name = sender.screen_name or f'user-{sender.id}'
    website_server_name = site.server_name

    recipients = [_get_user_address(recipient)]
    subject = (
        f'Mitteilung von {sender.screen_name} (über {website_server_name})'
    )
    body = _get_body(
        recipient.screen_name,
        sender_screen_name,
        text,
        sender_contact_url,
        website_server_name,
        email_config.contact_address,
    )

    return Message(email_config.sender, recipients, subject, body)


def _get_user(user_id: UserID) -> User:
    user = user_service.find_active_user(user_id)

    if user is None:
        raise ValueError(f"Unknown user ID '{user_id}' or account not active")

    return user


def _get_user_address(user: User) -> str:
    email_address = user_service.get_email_address(user.id)
    # If `name` evaluates to `False`, just the address is returned.
    return formataddr((user.screen_name, email_address))


def _get_body(
    recipient_screen_name: Optional[str],
    sender_screen_name: str,
    text: str,
    sender_contact_url: str,
    website_server_name: str,
    website_contact_address: Optional[str],
) -> str:
    body = f'''\
Hallo {recipient_screen_name},

{sender_screen_name} möchte dir die folgende Mitteilung zukommen lassen.

Du kannst hier antworten: {sender_contact_url}

ACHTUNG: Antworte *nicht* auf diese E-Mail, sondern folge dem Link.

---8<-------------------------------------

{text.strip()}

---8<-------------------------------------

-- 
Diese Mitteilung wurde über die Website {website_server_name} gesendet.'''

    if website_contact_address:
        body += f'\nBei Fragen kontaktiere uns bitte per E-Mail an: {website_contact_address}'

    return body
