"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from byceps.announce.announce import build_announcement_request
from byceps.byceps_app import BycepsApp
from byceps.services.newsletter.events import (
    SubscribedToNewsletterEvent,
    UnsubscribedFromNewsletterEvent,
)
from byceps.services.newsletter.models import ListID
from byceps.services.user.models.user import User

from .helpers import assert_text


def test_subscribed_to_newsletter_announced(
    app: BycepsApp, now: datetime, user: User, webhook_for_irc
):
    expected_text = 'User has subscribed to newsletter "CozyLAN Updates".'

    event = SubscribedToNewsletterEvent(
        occurred_at=now,
        initiator=user,
        user=user,
        list_id=ListID('cozylan-updates'),
        list_title='CozyLAN Updates',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_subscribed_to_newsletter_by_admin_announced(
    app: BycepsApp,
    now: datetime,
    admin_user: User,
    user: User,
    webhook_for_irc,
):
    expected_text = 'Admin has subscribed User to newsletter "CozyLAN Updates".'

    event = SubscribedToNewsletterEvent(
        occurred_at=now,
        initiator=admin_user,
        user=user,
        list_id=ListID('cozylan-updates'),
        list_title='CozyLAN Updates',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_unsubscribed_from_newsletter_announced(
    app: BycepsApp, now: datetime, user: User, webhook_for_irc
):
    expected_text = 'User has unsubscribed from newsletter "CozyLAN Updates".'

    event = UnsubscribedFromNewsletterEvent(
        occurred_at=now,
        initiator=user,
        user=user,
        list_id=ListID('cozylan-updates'),
        list_title='CozyLAN Updates',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_unsubscribed_from_newsletter_by_admin_announced(
    app: BycepsApp,
    now: datetime,
    admin_user: User,
    user: User,
    webhook_for_irc,
):
    expected_text = (
        'Admin has unsubscribed User from newsletter "CozyLAN Updates".'
    )

    event = UnsubscribedFromNewsletterEvent(
        occurred_at=now,
        initiator=admin_user,
        user=user,
        list_id=ListID('cozylan-updates'),
        list_title='CozyLAN Updates',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
