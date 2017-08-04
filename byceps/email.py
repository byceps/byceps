"""
byceps.email
~~~~~~~~~~~~

Sending e-mail.

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from flask_mail import Mail


_mail = Mail()


def init_app(app):
    _mail.init_app(app)


def send(recipients, subject, body, *, sender=None):
    message = {
        'recipients': recipients,
        'subject': subject,
        'body': body,
        'sender': sender,
    }

    _mail.send_message(**message)
