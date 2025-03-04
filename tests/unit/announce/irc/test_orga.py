"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.announce.announce import build_announcement_request
from byceps.byceps_app import BycepsApp
from byceps.services.core.events import EventBrand, EventUser
from byceps.services.orga.events import (
    OrgaStatusGrantedEvent,
    OrgaStatusRevokedEvent,
)

from .helpers import assert_text


def test_orga_status_granted_announced(
    app: BycepsApp,
    now: datetime,
    admin: EventUser,
    trainee: EventUser,
    brand: EventBrand,
    webhook_for_irc,
):
    expected_text = (
        'Admin has granted orga status for brand CozyLAN to Trainee.'
    )

    event = OrgaStatusGrantedEvent(
        occurred_at=now,
        initiator=admin,
        user=trainee,
        brand=brand,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_orga_status_revoked_announced(
    app: BycepsApp,
    now: datetime,
    admin: EventUser,
    trainee: EventUser,
    brand: EventBrand,
    webhook_for_irc,
):
    expected_text = (
        'Admin has revoked orga status for brand CozyLAN for Trainee.'
    )

    event = OrgaStatusRevokedEvent(
        occurred_at=now,
        initiator=admin,
        user=trainee,
        brand=brand,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def admin(make_event_user) -> EventUser:
    return make_event_user(screen_name='Admin')


@pytest.fixture(scope='module')
def trainee(make_event_user) -> EventUser:
    return make_event_user(screen_name='Trainee')


@pytest.fixture(scope='module')
def brand(make_event_brand) -> EventBrand:
    return make_event_brand(title='CozyLAN')
