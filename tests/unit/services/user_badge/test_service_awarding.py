"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.brand.models import BrandID
from byceps.services.user_badge import user_badge_domain_service
from byceps.services.user_badge.events import UserBadgeAwardedEvent
from byceps.services.user_badge.models import Badge, BadgeID

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
    assert event.initiator is None
    assert event.badge_id == badge.id
    assert event.badge_label == badge.label
    assert event.awardee.id == awardee.id
    assert event.awardee.screen_name == awardee.screen_name

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
    assert event.initiator is not None
    assert event.initiator.id == initiator.id
    assert event.initiator.screen_name == initiator.screen_name
    assert event.badge_id == badge.id
    assert event.badge_label == badge.label
    assert event.awardee.id == awardee.id
    assert event.awardee.screen_name == awardee.screen_name

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
def awardee(make_user):
    return make_user()


@pytest.fixture(scope='module')
def initiator(make_user):
    return make_user()
