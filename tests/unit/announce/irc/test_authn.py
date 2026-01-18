"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.announce.announce import build_announcement_request
from byceps.byceps_app import BycepsApp
from byceps.services.authn.events import (
    PasswordUpdatedEvent,
    UserLoggedInToAdminEvent,
    UserLoggedInToSiteEvent,
)

from .helpers import assert_text


def test_password_updated_announced(
    app: BycepsApp, now: datetime, make_user, webhook_for_irc
):
    expected_text = 'AuthAdmin has updated the password for ForgetfulFred.'

    event = PasswordUpdatedEvent(
        occurred_at=now,
        initiator=make_user(screen_name='AuthAdmin'),
        user=make_user(screen_name='ForgetfulFred'),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_user_logged_in_to_admin_app_announced(
    app: BycepsApp, now: datetime, make_user, webhook_for_irc
):
    expected_text = 'Logvogel has logged in to administration.'

    user = make_user(screen_name='Logvogel')

    event = UserLoggedInToAdminEvent(
        occurred_at=now,
        initiator=user,
        user=user,
        ip_address=None,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_user_logged_in_to_site_app_announced(
    app: BycepsApp,
    now: datetime,
    make_event_site,
    make_user,
    webhook_for_irc,
):
    expected_text = 'Logvogel has logged in to site "ACMECon 2014 website".'

    user = make_user(screen_name='Logvogel')

    event = UserLoggedInToSiteEvent(
        occurred_at=now,
        initiator=user,
        user=user,
        ip_address=None,
        site=make_event_site(title='ACMECon 2014 website'),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
