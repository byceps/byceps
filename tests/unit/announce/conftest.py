"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
from flask_babel import Babel
import pytest

from byceps.announce.connections import register_handlers


@pytest.fixture(scope='package')
def app():
    app = Flask('byceps')

    app.config['LOCALE'] = 'de'

    Babel(app)

    register_handlers()

    with app.app_context():
        yield app
