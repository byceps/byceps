"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.announce.announce import build_announcement_request
from byceps.byceps_app import BycepsApp
from byceps.events.base import EventUser
from byceps.events.external_accounts import (
    ExternalAccountConnectedEvent,
    ExternalAccountDisconnectedEvent,
)

from tests.helpers import generate_uuid

from .helpers import assert_text


def test_external_account_connected(
    app: BycepsApp,
    now: datetime,
    event_user: EventUser,
    webhook_for_irc,
):
    expected_text = 'Connector has connected an external account on "discord" for Connector.'

    event = ExternalAccountConnectedEvent(
        connected_external_account_id=generate_uuid(),
        occurred_at=now,
        initiator=event_user,
        user=event_user,
        service='discord',
        external_id=None,
        external_name=None,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_external_account_disconnected(
    app: BycepsApp,
    now: datetime,
    event_user: EventUser,
    webhook_for_irc,
):
    expected_text = 'Connector has disconnected an external account on "discord" for Connector.'

    event = ExternalAccountDisconnectedEvent(
        connected_external_account_id=generate_uuid(),
        occurred_at=now,
        initiator=event_user,
        user=event_user,
        service='discord',
        external_id=None,
        external_name=None,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def event_user(make_event_user) -> EventUser:
    return make_event_user(screen_name='Connector')
