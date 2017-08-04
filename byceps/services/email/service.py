"""
byceps.services.email.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from ... import email


def send_email(recipients, subject, body, *, sender=None):
    """Send an e-mail."""
    email.send(recipients, subject, body, sender=sender)
