"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.announce.announce import build_announcement_request
from byceps.events.authn import PasswordUpdatedEvent, UserLoggedInEvent
from byceps.events.base import EventSite, EventUser
from byceps.services.site.models import SiteID

from .helpers import assert_text, now


OCCURRED_AT = now()


def test_password_updated_announced(app: Flask, make_user, webhook_for_irc):
    expected_text = 'AuthAdmin has updated the password for ForgetfulFred.'

    event = PasswordUpdatedEvent(
        occurred_at=OCCURRED_AT,
        initiator=EventUser.from_user(make_user(screen_name='AuthAdmin')),
        user=make_user(screen_name='ForgetfulFred'),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_user_logged_in_into_admin_app_announced(
    app: Flask, make_user, webhook_for_irc
):
    expected_text = 'Logvogel has logged in.'

    event = UserLoggedInEvent(
        occurred_at=OCCURRED_AT,
        initiator=EventUser.from_user(make_user(screen_name='Logvogel')),
        site=None,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_user_logged_in_into_site_app_announced(
    app: Flask, make_user, webhook_for_irc
):
    expected_text = 'Logvogel has logged in on site "ACMECon 2014 website".'

    event = UserLoggedInEvent(
        occurred_at=OCCURRED_AT,
        initiator=EventUser.from_user(make_user(screen_name='Logvogel')),
        site=EventSite(SiteID('acmecon-2014'), 'ACMECon 2014 website'),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
