"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.events.user_badge import UserBadgeAwarded
from byceps.services.user import event_service
from byceps.services.user_badge import service as user_badge_service
from byceps.services.user_badge.transfer.models import QuantifiedBadgeAwarding

from ...conftest import database_recreated
from ...helpers import create_user


@pytest.fixture(scope='module')
def app(party_app, db):
    with party_app.app_context():
        with database_recreated(db):
            yield


def test_award_badge_without_initiator(app):
    user = create_user('EarlyPoster')

    badge = user_badge_service.create_badge(
        'first-post', 'First Post', 'first-post.svg'
    )

    user_events_before = event_service.get_events_for_user(user.id)
    assert len(user_events_before) == 0

    _, event = user_badge_service.award_badge_to_user(badge.id, user.id)

    assert event.__class__ is UserBadgeAwarded
    assert event.user_id == user.id
    assert event.badge_id == badge.id
    assert event.initiator_id is None

    user_events_after = event_service.get_events_for_user(user.id)
    assert len(user_events_after) == 1

    user_awarding_event = user_events_after[0]
    assert user_awarding_event.event_type == 'user-badge-awarded'
    assert user_awarding_event.data == {'badge_id': str(badge.id)}


def test_award_badge_with_initiator(app, admin_user):
    user = create_user('AwesomePerson')

    badge = user_badge_service.create_badge(
        'awesomeness', 'Certificate of Awesomeness', 'awesomeness.svg'
    )

    user_events_before = event_service.get_events_for_user(user.id)
    assert len(user_events_before) == 0

    _, event = user_badge_service.award_badge_to_user(
        badge.id, user.id, initiator_id=admin_user.id
    )

    assert event.__class__ is UserBadgeAwarded
    assert event.user_id == user.id
    assert event.badge_id == badge.id
    assert event.initiator_id == admin_user.id

    user_events_after = event_service.get_events_for_user(user.id)
    assert len(user_events_after) == 1

    user_awarding_event = user_events_after[0]
    assert user_awarding_event.event_type == 'user-badge-awarded'
    assert user_awarding_event.data == {
        'badge_id': str(badge.id),
        'initiator_id': str(admin_user.id),
    }


def test_get_awardings_of_unknown_badge(app):
    unknown_badge_id = '00000000-0000-0000-0000-000000000000'

    actual = user_badge_service.get_awardings_of_badge(unknown_badge_id)

    assert actual == set()


def test_get_awardings_of_unawarded_badge(app):
    badge = user_badge_service.create_badge(
        'eternal-wisdom', 'Eternal Wisdom', 'eternalwisdom.svg'
    )

    actual = user_badge_service.get_awardings_of_badge(badge.id)

    assert actual == set()


def test_get_awardings_of_badge():
    user1 = create_user('User1')
    user2 = create_user('User2')

    badge = user_badge_service.create_badge(
        'attendee', 'You were there.', 'attendance.svg'
    )

    user_badge_service.award_badge_to_user(badge.id, user1.id)
    user_badge_service.award_badge_to_user(badge.id, user1.id)
    user_badge_service.award_badge_to_user(badge.id, user2.id)

    actual = user_badge_service.get_awardings_of_badge(badge.id)

    assert actual == {
        QuantifiedBadgeAwarding(badge.id, user1.id, 2),
        QuantifiedBadgeAwarding(badge.id, user2.id, 1),
    }
