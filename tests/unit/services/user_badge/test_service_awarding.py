"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.events.user_badge import UserBadgeAwardedEvent
from byceps.services.user.models.user import User
from byceps.services.user_badge import user_badge_domain_service
from byceps.services.user_badge.models import Badge, BadgeID
from byceps.typing import BrandID, UserID

from tests.helpers import generate_token, generate_uuid


def test_award_badge_without_initiator(badge, awardee):
    awarding, event, log_entry = user_badge_domain_service.award_badge(
        badge, awardee
    )

    assert awarding.id is not None
    assert awarding.badge_id == badge.id
    assert awarding.awardee_id == awardee.id
    assert awarding.awarded_at is not None

    assert event.__class__ is UserBadgeAwardedEvent
    assert event.initiator_id is None
    assert event.initiator_screen_name is None
    assert event.badge_id == badge.id
    assert event.badge_label == badge.label
    assert event.awardee_id == awardee.id
    assert event.awardee_screen_name == awardee.screen_name

    assert log_entry.id is not None
    assert log_entry.occurred_at is not None
    assert log_entry.event_type == 'user-badge-awarded'
    assert log_entry.user_id == awardee.id
    assert log_entry.data == {
        'badge_id': str(badge.id),
    }


def test_award_badge_with_initiator(badge, awardee, initiator):
    awarding, event, log_entry = user_badge_domain_service.award_badge(
        badge, awardee, initiator=initiator
    )

    assert awarding.id is not None
    assert awarding.badge_id == badge.id
    assert awarding.awardee_id == awardee.id
    assert awarding.awarded_at is not None

    assert event.__class__ is UserBadgeAwardedEvent
    assert event.initiator_id == initiator.id
    assert event.initiator_screen_name == initiator.screen_name
    assert event.badge_id == badge.id
    assert event.badge_label == badge.label
    assert event.awardee_id == awardee.id
    assert event.awardee_screen_name == awardee.screen_name

    assert log_entry.id is not None
    assert log_entry.occurred_at is not None
    assert log_entry.event_type == 'user-badge-awarded'
    assert log_entry.user_id == awardee.id
    assert log_entry.data == {
        'badge_id': str(badge.id),
        'initiator_id': str(initiator.id),
    }


@pytest.fixture(scope='module')
def make_badge():
    def _wrapper(label: str, description: str) -> Badge:
        token = generate_token()
        return Badge(
            id=BadgeID(generate_uuid()),
            slug=token,
            label=label,
            description=description,
            image_filename=token,
            image_url_path=token,
            brand_id=BrandID(token),
            featured=False,
        )

    return _wrapper


@pytest.fixture(scope='module')
def badge(make_badge):
    return make_badge('awesomeness', 'Certificate of Awesomeness')


@pytest.fixture(scope='module')
def build_user():
    def _wrapper(*, suspended=False, deleted=False) -> User:
        return User(
            id=UserID(generate_uuid()),
            screen_name=None,
            suspended=suspended,
            deleted=deleted,
            locale=None,
            avatar_url=None,
        )

    return _wrapper


@pytest.fixture(scope='module')
def awardee(build_user):
    return build_user()


@pytest.fixture(scope='module')
def initiator(build_user):
    return build_user()
