"""
byceps.services.email.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional

from ...database import db, upsert
from ... import email
from ...typing import BrandID
from ...util.jobqueue import enqueue

from .models import EmailConfig as DbEmailConfig
from .transfer.models import Message, Sender


class EmailError(Exception):
    pass


def find_sender_for_brand(brand_id: BrandID) -> Optional[Sender]:
    """Return the configured sender for the brand."""
    config = DbEmailConfig.query.get(brand_id)

    if config is None:
        return None

    return Sender(
        config.sender_address,
        config.sender_name,
    )


def get_sender_for_brand(brand_id: BrandID) -> Sender:
    """Return the configured sender for the brand, or raise an error if
    none is configured for that brand ID.
    """
    sender = find_sender_for_brand(brand_id)

    if not sender:
        raise EmailError(
            'No sender configured for brand "{}".'.format(brand_id))

    return sender


def set_sender_for_brand(brand_id: BrandID, sender_address: str,
                         *, sender_name: Optional[str]=None) -> None:
    """Set the sender e-mail address for the brand."""
    table = DbEmailConfig.__table__
    identifier = {
        'brand_id': brand_id,
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
