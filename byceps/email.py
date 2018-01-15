"""
byceps.email
~~~~~~~~~~~~

Sending e-mail.

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List

from flask_mail import Mail


_mail = Mail()


def init_app(app):
    _mail.init_app(app)


def send(sender: str, recipients: List[str], subject: str, body: str) -> None:
    """Assemble and send an e-mail."""
    message = {
        'sender': sender,
        'recipients': recipients,
        'subject': subject,
        'body': body,
    }

    _mail.send_message(**message)
