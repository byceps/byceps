"""
byceps.services.email.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional

from ... import email
from ...typing import BrandID
from ...util.jobqueue import enqueue

from .models import EmailConfig


class EmailError(Exception):
    pass


def find_sender_address_for_brand(brand_id: BrandID) -> Optional[str]:
    """Return the configured sender e-mail address for the brand."""
    config = EmailConfig.query.get(brand_id)

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


def enqueue_email(sender: str, recipients: List[str], subject: str, body: str) \
                 -> None:
    """Enqueue an e-mail to be sent asynchronously."""
    enqueue(send_email, sender, recipients, subject, body)


def send_email(sender: str, recipients: List[str], subject: str, body: str) \
              -> None:
    """Send an e-mail."""
    email.send(sender, recipients, subject, body)
