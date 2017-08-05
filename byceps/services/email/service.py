"""
byceps.services.email.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List, Optional

from ... import email


def send_email(recipients: List[str], subject: str, body: str, *,
               sender: Optional[str]=None) -> None:
    """Send an e-mail."""
    email.send(recipients, subject, body, sender=sender)
