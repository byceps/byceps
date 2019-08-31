"""
byceps.services.email.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional

from ...database import db, upsert
from ... import email
from ...util.jobqueue import enqueue

from .models import EmailConfig as DbEmailConfig
from .transfer.models import Message, Sender


class EmailError(Exception):
    pass


def find_sender(config_id: str) -> Optional[Sender]:
    """Return the configured sender."""
    config = DbEmailConfig.query.get(config_id)

    if config is None:
        return None

    return Sender(
        config.sender_address,
        config.sender_name,
    )


def get_sender(config_id: str) -> Sender:
    """Return the configured sender, or raise an error if none is
    configured for that ID.
    """
    sender = find_sender(config_id)

    if not sender:
        raise EmailError('No sender configured for ID "{}".'.format(config_id))

    return sender


def set_sender(config_id: str, sender_address: str,
               *, sender_name: Optional[str]=None) -> None:
    """Set sender e-mail address and name for a config."""
    table = DbEmailConfig.__table__
    identifier = {
        'id': config_id,
        'sender_address': sender_address,
    }
    replacement = {
        'sender_name': sender_name,
    }

    upsert(table, identifier, replacement)


def enqueue_message(message: Message) -> None:
    """Enqueue e-mail to be sent asynchronously."""
    enqueue_email(
        message.sender,
        message.recipients,
        message.subject,
        message.body)


def enqueue_email(sender: Sender, recipients: List[str], subject: str,
                  body: str) -> None:
    """Enqueue e-mail to be sent asynchronously."""
    enqueue(send_email, sender.format(), recipients, subject, body)


def send_email(sender: str, recipients: List[str], subject: str, body: str) \
              -> None:
    """Send e-mail."""
    email.send(sender, recipients, subject, body)
