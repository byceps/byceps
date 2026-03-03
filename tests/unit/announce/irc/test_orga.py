"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

import pytest

from byceps.announce.announce import build_announcement_request
from byceps.byceps_app import BycepsApp
from byceps.services.core.events import EventBrand
from byceps.services.orga.events import (
    OrgaStatusGrantedEvent,
    OrgaStatusRevokedEvent,
)
from byceps.services.user.models import User

from .helpers import assert_text


def test_orga_status_granted_announced(
    app: BycepsApp,
    now: datetime,
    admin_user: User,
    trainee: User,
    brand: EventBrand,
    webhook_for_irc,
):
    expected_text = (
        'Admin has granted orga status for brand CozyLAN to Trainee.'
    )

    event = OrgaStatusGrantedEvent(
        occurred_at=now,
        initiator=admin_user,
        user=trainee,
        brand=brand,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_orga_status_revoked_announced(
    app: BycepsApp,
    now: datetime,
    admin_user: User,
    trainee: User,
    brand: EventBrand,
    webhook_for_irc,
):
    expected_text = (
        'Admin has revoked orga status for brand CozyLAN for Trainee.'
    )

    event = OrgaStatusRevokedEvent(
        occurred_at=now,
        initiator=admin_user,
        user=trainee,
        brand=brand,
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def trainee(make_user) -> User:
    return make_user(screen_name='Trainee')


@pytest.fixture(scope='module')
def brand(make_event_brand) -> EventBrand:
    return make_event_brand(title='CozyLAN')
