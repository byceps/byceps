"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps import config_defaults
from byceps.email import _get_config


def test_get_config_with_defaults():
    app = create_app()

    actual = _get_config(app)

    assert actual == {
        'transport.use': 'smtp',
        'transport.host': 'localhost',
        'transport.port': 25,
        'transport.debug': False,
        'message.author': 'BYCEPS <noreply@byceps.example>',
    }


def test_get_config_with_custom_values():
    app = create_app()
    app.config.update(
        {
            'MAIL_SERVER': 'mail.server.example',
            'MAIL_PORT': 2525,
            'MAIL_DEBUG': True,
            'MAIL_DEFAULT_SENDER': 'Mailer <noreply@server.example>',
            'MAIL_USERNAME': 'paperboy',
            'MAIL_PASSWORD': 'secret!',
        }
    )

    actual = _get_config(app)

    assert actual == {
        'transport.use': 'smtp',
        'transport.host': 'mail.server.example',
        'transport.port': 2525,
        'transport.debug': True,
        'transport.username': 'paperboy',
        'transport.password': 'secret!',
        'message.author': 'Mailer <noreply@server.example>',
    }


def test_get_config_with_ssl():
    app = create_app()
    app.config['MAIL_USE_SSL'] = True

    actual = _get_config(app)

    assert actual['transport.tls'] == 'ssl'


def test_get_config_with_tls():
    app = create_app()
    app.config['MAIL_USE_TLS'] = True

    actual = _get_config(app)

    assert actual['transport.tls'] == 'required'


def test_get_config_with_ssl_and_tls():
    # Can only be set to SSL or TLS.
    # If both are requested, TLS wins.

    app = create_app()
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USE_TLS'] = True

    actual = _get_config(app)

    assert actual['transport.tls'] == 'required'


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_defaults)
    return app
