"""
byceps.services.user_message.user_message_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Send an e-mail message from one user to another.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from email.utils import formataddr
from typing import Optional

from flask_babel import gettext

from byceps.services.email import email_config_service, email_service
from byceps.services.email.models import Message
from byceps.services.site import site_service
from byceps.services.site.models import SiteID
from byceps.services.user import user_service
from byceps.services.user.models.user import User
from byceps.typing import UserID
from byceps.util.l10n import force_user_locale


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
    email_config = email_config_service.get_config(site.brand_id)

    recipients = [_get_user_address(recipient)]

    sender_screen_name = sender.screen_name or f'user-{sender.id}'
    website_server_name = site.server_name

    with force_user_locale(recipient):
        subject = _get_subject(sender_screen_name, website_server_name)
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


def _get_subject(sender_screen_name: str, website_server_name: str) -> str:
    return gettext(
        'Message from %(sender_screen_name)s (via %(website_server_name)s)',
        sender_screen_name=sender_screen_name,
        website_server_name=website_server_name,
    )


def _get_body(
    recipient_screen_name: Optional[str],
    sender_screen_name: str,
    text: str,
    sender_contact_url: str,
    website_server_name: str,
    website_contact_address: Optional[str],
) -> str:
    paragraphs = [
        gettext('Hello %(screen_name)s,', screen_name=recipient_screen_name),
        gettext(
            '%(screen_name)s has sent you the following message.',
            screen_name=sender_screen_name,
        ),
        gettext('You can reply here: %(url)s', url=sender_contact_url),
        gettext(
            'ATTENTION: Do *not* reply to this email. Follow the link instead.'
        ),
        '---8<-------------------------------------',
        text.strip(),
        '---8<-------------------------------------',
        '-- \n'
        + gettext(
            'This message was sent via website %(server_name)s.',
            server_name=website_server_name,
        ),
    ]

    body = '\n\n'.join(paragraphs)
    if website_contact_address:
        body += '\n' + gettext(
            'If you have any questions, please contact us via email to: %(email_address)s',
            email_address=website_contact_address,
        )

    return body
