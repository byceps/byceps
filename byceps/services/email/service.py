"""
byceps.services.email.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional

from sqlalchemy.dialects.postgresql import insert

from ...database import db
from ... import email
from ...typing import BrandID
from ...util.jobqueue import enqueue

from .models import EmailConfig as DbEmailConfig
from .transfer.models import Message


class EmailError(Exception):
    pass


def find_sender_address_for_brand(brand_id: BrandID) -> Optional[str]:
    """Return the configured sender e-mail address for the brand."""
    config = DbEmailConfig.query.get(brand_id)

    if config is None:
        return None

    return config.sender_address


def get_sender_address_for_brand(brand_id: BrandID) -> str:
    """Return the configured sender e-mail address for the brand, or
    raise an error if none is configured for that brand ID.
    """
    sender_address = find_sender_address_for_brand(brand_id)

    if not sender_address:
        raise EmailError(
            'No sender address configured for brand "{}".'.format(brand_id))

    return sender_address


def set_sender_address_for_brand(brand_id: BrandID, sender_address: str
                                ) -> None:
    """Set the sender e-mail address for the brand."""
    table = DbEmailConfig.__table__

    # UPSERT
    query = insert(table) \
        .values(
            brand_id=brand_id,
            sender_address=sender_address
        ) \
        .on_conflict_do_update(
            constraint=table.primary_key,
            set_={'sender_address': sender_address})

    db.session.execute(query)
    db.session.commit()


def enqueue_message(message: Message) -> None:
    """Enqueue e-mail to be sent asynchronously."""
    enqueue_email(
        message.sender,
        message.recipients,
        message.subject,
        message.body)


def enqueue_email(sender: str, recipients: List[str], subject: str, body: str) \
                 -> None:
    """Enqueue e-mail to be sent asynchronously."""
    enqueue(send_email, sender, recipients, subject, body)


def send_email(sender: str, recipients: List[str], subject: str, body: str) \
              -> None:
    """Send e-mail."""
    email.send(sender, recipients, subject, body)
