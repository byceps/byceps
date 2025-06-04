"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.announce.announce import build_announcement_request
from byceps.byceps_app import BycepsApp
from byceps.services.core.events import EventUser
from byceps.services.newsletter.events import (
    SubscribedToNewsletterEvent,
    UnsubscribedFromNewsletterEvent,
)
from byceps.services.newsletter.models import ListID

from .helpers import assert_text


def test_subscribed_to_newsletter_announced(
    app: BycepsApp, now: datetime, user: EventUser, webhook_for_irc
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
    admin: EventUser,
    user: EventUser,
    webhook_for_irc,
):
    expected_text = 'Admin has subscribed User to newsletter "CozyLAN Updates".'

    event = SubscribedToNewsletterEvent(
        occurred_at=now,
        initiator=admin,
        user=user,
        list_id=ListID('cozylan-updates'),
        list_title='CozyLAN Updates',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_unsubscribed_from_newsletter_announced(
    app: BycepsApp, now: datetime, user: EventUser, webhook_for_irc
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
    admin: EventUser,
    user: EventUser,
    webhook_for_irc,
):
    expected_text = (
        'Admin has unsubscribed User from newsletter "CozyLAN Updates".'
    )

    event = UnsubscribedFromNewsletterEvent(
        occurred_at=now,
        initiator=admin,
        user=user,
        list_id=ListID('cozylan-updates'),
        list_title='CozyLAN Updates',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def admin(make_event_user) -> EventUser:
    return make_event_user(screen_name='Admin')


@pytest.fixture(scope='module')
def user(make_event_user) -> EventUser:
    return make_event_user(screen_name='User')
