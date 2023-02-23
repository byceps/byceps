"""
byceps.services.email.email_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from email.message import EmailMessage
from email.utils import parseaddr
from smtplib import SMTP

from flask import current_app

from ...util.jobqueue import enqueue

from .models import Message, NameAndAddress


def parse_address(address_str: str) -> NameAndAddress:
    """Parse a string into name and address parts."""
    name, address = parseaddr(address_str)

    if not name and not address:
        raise ValueError(f'Could not parse name and address value: "{address}"')

    return NameAndAddress(name, address)


def enqueue_message(message: Message) -> None:
    """Enqueue e-mail to be sent asynchronously."""
    enqueue_email(
        message.sender, message.recipients, message.subject, message.body
    )


def enqueue_email(
    sender: NameAndAddress,
    recipients: list[str],
    subject: str,
    body: str,
) -> None:
    """Enqueue e-mail to be sent asynchronously."""
    sender_str = sender.format()
    enqueue(send_email, sender_str, recipients, subject, body)


def send_email(
    sender: str, recipients: list[str], subject: str, body: str
) -> None:
    """Send e-mail."""
    send(sender, recipients, subject, body)


def send(sender: str, recipients: list[str], subject: str, body: str) -> None:
    """Assemble and send e-mail."""
    if current_app.config.get('MAIL_SUPPRESS_SEND', False):
        current_app.logger.debug('Suppressing sending of email.')
        return

    message = _build_message(sender, recipients, subject, body)

    current_app.logger.debug('Sending email.')
    _send_via_smtp(message)


def _build_message(
    sender: str, recipients: list[str], subject: str, body: str
) -> EmailMessage:
    """Assemble message."""
    message = EmailMessage()
    message['From'] = sender
    message['To'] = ', '.join(recipients)
    message['Subject'] = subject
    message.set_content(body)
    return message


def _send_via_smtp(message: EmailMessage) -> None:
    """Send email via SMTP."""
    config = current_app.config

    host = config.get('MAIL_HOST', 'localhost')
    port = config.get('MAIL_PORT', 25)
    starttls = config.get('MAIL_STARTTLS', False)
    username = config.get('MAIL_USERNAME', None)
    password = config.get('MAIL_PASSWORD', None)

    with SMTP(host, port) as smtp:
        if starttls:
            smtp.starttls()

        if username and password:
            smtp.login(username, password)

        smtp.send_message(message)
