"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
import pytest

from byceps.announce.announce import build_announcement_request
from byceps.events.base import EventUser
from byceps.events.newsletter import (
    SubscribedToNewsletterEvent,
    UnsubscribedFromNewsletterEvent,
)
from byceps.services.newsletter.models import ListID
from byceps.services.user.models.user import User

from .helpers import assert_text, now


OCCURRED_AT = now()


def test_subscribed_to_newsletter_announced(
    app: Flask, user: User, webhook_for_irc
):
    expected_text = 'User has subscribed to newsletter "CozyLAN Updates".'

    event = SubscribedToNewsletterEvent(
        occurred_at=OCCURRED_AT,
        initiator=EventUser.from_user(user),
        user=EventUser.from_user(user),
        list_id=ListID('cozylan-updates'),
        list_title='CozyLAN Updates',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_unsubscribed_from_newsletter_announced(
    app: Flask, user: User, webhook_for_irc
):
    expected_text = 'User has unsubscribed from newsletter "CozyLAN Updates".'

    event = UnsubscribedFromNewsletterEvent(
        occurred_at=OCCURRED_AT,
        initiator=EventUser.from_user(user),
        user=EventUser.from_user(user),
        list_id=ListID('cozylan-updates'),
        list_title='CozyLAN Updates',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def user(make_user) -> User:
    return make_user(screen_name='User')
