"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.announce.announce import build_announcement_request
from byceps.byceps_app import BycepsApp
from byceps.services.user_badge.events import UserBadgeAwardedEvent
from byceps.services.user_badge.models import BadgeID

from tests.helpers import generate_uuid

from .helpers import assert_text


BADGE_ID = BadgeID(generate_uuid())


def test_user_badge_awarding_announced_without_initiator(
    app: BycepsApp, now: datetime, make_user, webhook_for_irc
):
    expected_text = 'Someone has awarded badge "First Post!" to Erster.'

    event = UserBadgeAwardedEvent(
        occurred_at=now,
        initiator=None,
        badge_id=BADGE_ID,
        badge_label='First Post!',
        awardee=make_user(screen_name='Erster'),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_user_badge_awarding_announced_with_initiator(
    app: BycepsApp, now: datetime, make_user, webhook_for_irc
):
    expected_text = 'Admin has awarded badge "Glanzleistung" to PathFinder.'

    event = UserBadgeAwardedEvent(
        occurred_at=now,
        initiator=make_user(screen_name='Admin'),
        badge_id=BADGE_ID,
        badge_label='Glanzleistung',
        awardee=make_user(screen_name='PathFinder'),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
