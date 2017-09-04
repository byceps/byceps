"""
byceps.services.email.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
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


def enqueue_email(recipients: List[str], subject: str, body: str, *,
               sender: Optional[str]=None) -> None:
    """Enqueue an e-mail to be sent asynchronously."""
    enqueue(send_email, recipients, subject, body, sender=sender)


def send_email(recipients: List[str], subject: str, body: str, *,
               sender: Optional[str]=None) -> None:
    """Send an e-mail."""
    email.send(recipients, subject, body, sender=sender)
