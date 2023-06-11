"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.announce.connections import build_announcement_request
from byceps.events.user_badge import UserBadgeAwardedEvent
from byceps.services.user_badge.models import BadgeID
from byceps.typing import UserID

from tests.helpers import generate_uuid

from .helpers import assert_text, now


OCCURRED_AT = now()
ADMIN_ID = UserID(generate_uuid())
BADGE_ID = BadgeID(generate_uuid())
AWARDEE_ID = UserID(generate_uuid())


def test_user_badge_awarding_announced_without_initiator(
    app: Flask, webhook_for_irc
):
    expected_text = (
        'Jemand hat das Abzeichen "First Post!" an Erster verliehen.'
    )

    event = UserBadgeAwardedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=None,
        initiator_screen_name=None,
        badge_id=BADGE_ID,
        badge_label='First Post!',
        awardee_id=AWARDEE_ID,
        awardee_screen_name='Erster',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_user_badge_awarding_announced_with_initiator(
    app: Flask, webhook_for_irc
):
    expected_text = (
        'Admin hat das Abzeichen "Glanzleistung" an PathFinder verliehen.'
    )

    event = UserBadgeAwardedEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=ADMIN_ID,
        initiator_screen_name='Admin',
        badge_id=BADGE_ID,
        badge_label='Glanzleistung',
        awardee_id=AWARDEE_ID,
        awardee_screen_name='PathFinder',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
