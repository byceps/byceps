"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask

from byceps.announce.announce import build_announcement_request
from byceps.events.newsletter import (
    SubscribedToNewsletterEvent,
    UnsubscribedFromNewsletterEvent,
)
from byceps.services.newsletter.models import ListID
from byceps.typing import UserID

from tests.helpers import generate_uuid

from .helpers import assert_text, now


OCCURRED_AT = now()
USER_ID = UserID(generate_uuid())


def test_subscribed_to_newsletter_announced(app: Flask, webhook_for_irc):
    expected_text = 'Gast hat den Newsletter "CozyLAN-Updates" abonniert.'

    event = SubscribedToNewsletterEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=USER_ID,
        initiator_screen_name='Gast',
        user_id=USER_ID,
        user_screen_name='Gast',
        list_id=ListID('cozylan-updates'),
        list_title='CozyLAN-Updates',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_unsubscribed_from_newsletter_announced(app: Flask, webhook_for_irc):
    expected_text = 'Gast hat den Newsletter "CozyLAN-Updates" abbestellt.'

    event = UnsubscribedFromNewsletterEvent(
        occurred_at=OCCURRED_AT,
        initiator_id=USER_ID,
        initiator_screen_name='Gast',
        user_id=USER_ID,
        user_screen_name='Gast',
        list_id=ListID('cozylan-updates'),
        list_title='CozyLAN-Updates',
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)
