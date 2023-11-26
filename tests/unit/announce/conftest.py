"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest


@pytest.fixture(scope='package')
def app(make_app):
    app = make_app(additional_config={'LOCALE': 'en'})
    with app.app_context():
        yield app


def now() -> datetime:
    return datetime.utcnow()
