"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.announce.connections import build_announcement_request
from byceps.events.auth import UserLoggedInEvent
from byceps.services.site.models import SiteID
from byceps.typing import UserID

from tests.helpers import generate_uuid

from .helpers import build_announcement_request_for_irc, now


OCCURRED_AT = now()
USER_ID = UserID(generate_uuid())


def test_user_logged_in_into_admin_app_announced(app: Flask, webhook_for_irc):
    expected_text = 'Logvogel hat sich eingeloggt.'
    expected = build_announcement_request_for_irc(expected_text)

    event = UserLoggedInEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=USER_ID,
        initiator_screen_name='Logvogel',
        site_id=None,
        site_title=None,
    )

    assert build_announcement_request(event, webhook_for_irc) == expected


def test_user_logged_in_into_site_app_announced(app: Flask, webhook_for_irc):
    expected_text = (
        'Logvogel hat sich auf Site "ACMECon 2014 website" eingeloggt.'
    )
    expected = build_announcement_request_for_irc(expected_text)

    event = UserLoggedInEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=USER_ID,
        initiator_screen_name='Logvogel',
        site_id=SiteID('acmecon-2014'),
        site_title='ACMECon 2014 website',
    )

    assert build_announcement_request(event, webhook_for_irc) == expected
