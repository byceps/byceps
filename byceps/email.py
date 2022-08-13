"""
byceps.email
~~~~~~~~~~~~

Send e-mail.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from email.message import EmailMessage
from smtplib import SMTP

from flask import current_app


def send(sender: str, recipients: list[str], subject: str, body: str) -> None:
    """Assemble and send an e-mail."""
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
    username = config.get('MAIL_USERNAME', None)
    password = config.get('MAIL_PASSWORD', None)

    with SMTP(host, port) as smtp:
        if username and password:
            smtp.login(username, password)

        smtp.send_message(message)
