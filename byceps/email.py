"""
byceps.email
~~~~~~~~~~~~

Sending e-mail.

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import List

from flask_marrowmailer import Mailer


_mailer = Mailer()


def init_app(app):
    marrowmailer_config_key = 'MARROWMAILER_CONFIG'
    if marrowmailer_config_key not in app.config:
        app.config[marrowmailer_config_key] = _get_config(app)

    _mailer.init_app(app)


def _get_config(app):
    if app.config.get('MAIL_SUPPRESS_SEND', False) or app.testing:
        return {
            'transport.use': 'mock',
        }

    config = {
        'transport.use': 'smtp',
        'transport.host': app.config.get('MAIL_SERVER', 'localhost'),
        'transport.port': app.config.get('MAIL_PORT', 25),
        'transport.debug': app.config.get('MAIL_DEBUG', app.debug),
        'message.author': app.config.get('MAIL_DEFAULT_SENDER', None),
    }

    username = app.config.get('MAIL_USERNAME', None)
    if username is not None:
        config['transport.username'] = username

    password = app.config.get('MAIL_PASSWORD', None)
    if password is not None:
        config['transport.password'] = password

    if app.config.get('MAIL_USE_SSL', False):
        config['transport.tls'] = 'ssl'

    if app.config.get('MAIL_USE_TLS', False):
        config['transport.tls'] = 'required'

    return config


def send(sender: str, recipients: List[str], subject: str, body: str) -> None:
    """Assemble and send an e-mail."""
    message = _mailer.new(
        author=sender,
        to=recipients,
        subject=subject,
        plain=body,
        brand=False)

    _mailer.send(message)
