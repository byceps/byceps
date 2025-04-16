"""
byceps.services.email.email_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import parseaddr
from smtplib import SMTP, SMTP_SSL

from flask import current_app
import structlog

from byceps.util.jobqueue import enqueue
from byceps.util.result import Err, Ok, Result

from .models import Message, NameAndAddress


log = structlog.get_logger()


@dataclass(frozen=True)
class SmtpConfig:
    host: str
    port: int
    starttls: bool
    use_ssl: bool
    username: str | None
    password: str | None
    suppress_send: bool


def parse_address(address_str: str) -> Result[NameAndAddress, str]:
    """Parse a string into name and address parts."""
    name, address = parseaddr(address_str)

    if not name and not address:
        return Err(f'Could not parse name and address value: "{address}"')

    return Ok(NameAndAddress(name, address))


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
    smtp_config = current_app.byceps_config.smtp

    if smtp_config.suppress_send:
        log.debug('Suppressing sending of email.')
        return

    message = _build_message(sender, recipients, subject, body)

    log.debug('Sending email.')
    _send_via_smtp(smtp_config, message)


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


def _send_via_smtp(smtp_config: SmtpConfig, message: EmailMessage) -> None:
    """Send email via SMTP."""
    if smtp_config.use_ssl:
        _send_via_smtp_with_ssl(smtp_config, message)
    else:
        _send_via_smtp_without_ssl(smtp_config, message)


def _send_via_smtp_with_ssl(
    smtp_config: SmtpConfig, message: EmailMessage
) -> None:
    """Send email via SMTP with SSL."""
    with SMTP_SSL(smtp_config.host, smtp_config.port) as smtp:
        if smtp_config.username and smtp_config.password:
            smtp.login(smtp_config.username, smtp_config.password)

        smtp.send_message(message)


def _send_via_smtp_without_ssl(
    smtp_config: SmtpConfig, message: EmailMessage
) -> None:
    """Send email via SMTP without SSL (but potentially with STARTTLS)."""
    with SMTP(smtp_config.host, smtp_config.port) as smtp:
        if smtp_config.starttls:
            smtp.starttls()

        if smtp_config.username and smtp_config.password:
            smtp.login(smtp_config.username, smtp_config.password)

        smtp.send_message(message)
