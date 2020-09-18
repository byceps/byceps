"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.global_setting import service as global_settings_service


@pytest.fixture(scope='module')
def app(admin_app):
    global_settings_service.create_setting('announce_irc_delay', 0)
    global_settings_service.create_setting('announce_irc_enabled', 'true')
    global_settings_service.create_setting(
        'announce_irc_webhook_url', 'http://127.0.0.1:12345/'
    )

    yield admin_app

    global_settings_service.remove_setting('announce_irc_delay')
    global_settings_service.remove_setting('announce_irc_enabled')
    global_settings_service.remove_setting('announce_irc_webhook_url')
