"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from flask import Flask
import pytest

from byceps.announce.announce import build_announcement_request
from byceps.events.base import EventBrand, EventUser
from byceps.events.orga import OrgaStatusGrantedEvent, OrgaStatusRevokedEvent
from byceps.services.brand.models import BrandID
from byceps.services.user.models.user import User

from .helpers import assert_text, now


OCCURRED_AT = now()


def test_orga_status_granted_announced(
    app: Flask, admin: User, trainee: User, webhook_for_irc
):
    expected_text = (
        'Admin has granted orga status for brand CozyLAN to Trainee.'
    )

    event = OrgaStatusGrantedEvent(
        occurred_at=OCCURRED_AT,
        initiator=EventUser.from_user(admin),
        user=EventUser.from_user(trainee),
        brand=EventBrand(BrandID('cozylan'), 'CozyLAN'),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


def test_orga_status_revoked_announced(
    app: Flask, admin: User, trainee: User, webhook_for_irc
):
    expected_text = (
        'Admin has revoked orga status for brand CozyLAN for Trainee.'
    )

    event = OrgaStatusRevokedEvent(
        occurred_at=OCCURRED_AT,
        initiator=EventUser.from_user(admin),
        user=EventUser.from_user(trainee),
        brand=EventBrand(BrandID('cozylan'), 'CozyLAN'),
    )

    actual = build_announcement_request(event, webhook_for_irc)

    assert_text(actual, expected_text)


# helpers


@pytest.fixture(scope='module')
def admin(make_user) -> User:
    return make_user(screen_name='Admin')


@pytest.fixture(scope='module')
def trainee(make_user) -> User:
    return make_user(screen_name='Trainee')
