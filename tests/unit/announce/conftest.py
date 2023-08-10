"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest


@pytest.fixture(scope='package')
def app(make_app):
    app = make_app(additional_config={'LOCALE': 'de'})
    with app.app_context():
        yield app
