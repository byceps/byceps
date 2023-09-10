"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.announce.announce import build_announcement_request
from byceps.events.orga import OrgaStatusGrantedEvent, OrgaStatusRevokedEvent
from byceps.typing import BrandID, UserID

from tests.helpers import generate_uuid

from .helpers import assert_text, now


OCCURRED_AT = now()
ADMIN_ID = UserID(generate_uuid())
USER_ID = UserID(generate_uuid())


def test_orga_status_granted_announced(app: Flask, webhook_for_irc):
    expected_text = (
        'Admin hat Trainee den Orga-Status für die Marke CozyLAN verliehen.'
    )

    event = OrgaStatusGrantedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ADMIN_ID,
        initiator_screen_name='Admin',
        user_id=USER_ID,
        user_screen_name='Trainee',
        brand_id=BrandID('cozylan'),
        brand_title='CozyLAN',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_orga_status_revoked_announced(app: Flask, webhook_for_irc):
    expected_text = (
        'Admin hat Trainee den Orga-Status für die Marke CozyLAN entzogen.'
    )

    event = OrgaStatusRevokedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ADMIN_ID,
        initiator_screen_name='Admin',
        user_id=USER_ID,
        user_screen_name='Trainee',
        brand_id=BrandID('cozylan'),
        brand_title='CozyLAN',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
