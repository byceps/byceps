"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest


@pytest.fixture(scope='session')
def app(admin_app):
    admin_app.config.update({
        'ANNOUNCE_IRC_ENABLED': True,
        'ANNOUNCE_IRC_TEXT_PREFIX': '',
        'ANNOUNCE_IRC_DELAY': 0,
    })

    yield admin_app
