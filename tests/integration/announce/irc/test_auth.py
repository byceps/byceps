"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.announce.connections import build_announcement_request
from byceps.services.authentication.session import authn_session_service

from .helpers import build_announcement_request_for_irc


def test_user_logged_in_into_admin_app_announced(
    admin_app, user, webhook_for_irc
):
    expected_text = 'Logvogel hat sich eingeloggt.'
    expected = build_announcement_request_for_irc(expected_text)

    _, event = authn_session_service.log_in_user(user.id)

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_user_logged_in_into_site_app_announced(
    admin_app, site, user, webhook_for_irc
):
    expected_text = (
        'Logvogel hat sich auf Site "ACMECon 2014 website" eingeloggt.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    _, event = authn_session_service.log_in_user(user.id, site_id=site.id)

    assert build_announcement_request(event, webhook_for_irc) == expected


# helpers


@pytest.fixture(scope='module')
def user(make_user):
    return make_user('Logvogel')
