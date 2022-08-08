"""
byceps.services.email.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from email.utils import parseaddr

from ... import email
from ...util.jobqueue import enqueue

from .transfer.models import Message, NameAndAddress


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
    email.send(sender, recipients, subject, body)
