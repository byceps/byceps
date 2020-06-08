"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest


@pytest.fixture(scope='module')
def app(admin_app):
    admin_app.config['ANNOUNCE_IRC_ENABLED'] = True
    admin_app.config['ANNOUNCE_IRC_TEXT_PREFIX'] = ''
    yield admin_app
