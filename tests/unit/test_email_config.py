"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.email import _get_config


def test_get_config_with_defaults():
    app = Flask(__name__)

    actual = _get_config(app)

    assert actual == {
        'transport.use': 'smtp',
        'transport.host': 'localhost',
        'transport.port': 25,
        'transport.debug': False,
        'message.author': None,
    }


def test_get_config_with_custom_values():
    app = Flask(__name__)
    app.config.update({
        'MAIL_SERVER': 'mail.server.example',
        'MAIL_PORT': 2525,
        'MAIL_DEBUG': True,
        'MAIL_DEFAULT_SENDER': 'Mailer <noreply@server.example>',
        'MAIL_USERNAME': 'paperboy',
        'MAIL_PASSWORD': 'secret!',
    })

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
    app = Flask(__name__)
    app.config['MAIL_USE_SSL'] = True

    actual = _get_config(app)

    assert actual['transport.tls'] == 'ssl'


def test_get_config_with_tls():
    app = Flask(__name__)
    app.config['MAIL_USE_TLS'] = True

    actual = _get_config(app)

    assert actual['transport.tls'] == 'required'


def test_get_config_with_ssl_and_tls():
    # Can only be set to SSL or TLS.
    # If both are requested, TLS wins.

    app = Flask(__name__)
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USE_TLS'] = True

    actual = _get_config(app)

    assert actual['transport.tls'] == 'required'
