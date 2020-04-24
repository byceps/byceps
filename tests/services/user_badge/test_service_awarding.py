"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.events.user_badge import UserBadgeAwarded
from byceps.services.user import event_service
from byceps.services.user_badge import (
    command_service as badge_command_service,
    service as badge_service,
)
from byceps.services.user_badge.models.awarding import (
    BadgeAwarding as DbBadgeAwarding,
)
from byceps.services.user_badge.transfer.models import QuantifiedBadgeAwarding


@pytest.fixture(scope='module')
def user1(make_user):
    yield from make_user('Stullenandi')


@pytest.fixture(scope='module')
def user2(make_user):
    yield from make_user('Anica')


@pytest.fixture(scope='module')
def user3(make_user):
    yield from make_user('Slobo')


@pytest.fixture(scope='module')
def badge1():
    return _create_badge('attendance', 'You were there.')


@pytest.fixture(scope='module')
def badge2():
    return _create_badge('awesomeness', 'Certificate of Awesomeness')


@pytest.fixture(scope='module')
def badge3():
    return _create_badge('eternal-wisdom', 'Eternal Wisdom')


@pytest.fixture
def awardings_scope(db):
    yield

    # Remove badge awardings.
    db.session.query(DbBadgeAwarding).delete()
    db.session.commit()


def test_award_badge_without_initiator(
    party_app, user1, badge1, awardings_scope
):
    user = user1
    badge = badge1

    user_events_before = event_service.get_events_for_user(user.id)
    assert len(user_events_before) == 0

    _, event = badge_command_service.award_badge_to_user(badge.id, user.id)

    assert event.__class__ is UserBadgeAwarded
    assert event.user_id == user.id
    assert event.badge_id == badge.id
    assert event.initiator_id is None

    user_events_after = event_service.get_events_for_user(user.id)
    assert len(user_events_after) == 1

    user_awarding_event = user_events_after[0]
    assert user_awarding_event.event_type == 'user-badge-awarded'
    assert user_awarding_event.data == {'badge_id': str(badge.id)}


def test_award_badge_with_initiator(
    party_app, user2, badge2, admin_user, awardings_scope
):
    user = user2

    badge = badge2

    user_events_before = event_service.get_events_for_user(user.id)
    assert len(user_events_before) == 0

    _, event = badge_command_service.award_badge_to_user(
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


def test_count_awardings(
    party_app,
    user1,
    user2,
    user3,
    badge1,
    badge2,
    badge3,
    awardings_scope,
):
    badge_command_service.award_badge_to_user(badge1.id, user1.id)
    badge_command_service.award_badge_to_user(badge1.id, user1.id)
    badge_command_service.award_badge_to_user(badge1.id, user2.id)
    badge_command_service.award_badge_to_user(badge1.id, user3.id)
    badge_command_service.award_badge_to_user(badge3.id, user2.id)
    badge_command_service.award_badge_to_user(badge3.id, user3.id)

    actual = badge_service.count_awardings()

    assert actual == {badge1.id: 4, badge2.id: 0, badge3.id: 2}


def test_get_awardings_of_unknown_badge(party_app):
    unknown_badge_id = '00000000-0000-0000-0000-000000000000'

    actual = badge_service.get_awardings_of_badge(unknown_badge_id)

    assert actual == set()


def test_get_awardings_of_unawarded_badge(party_app, badge3):
    badge = badge3

    actual = badge_service.get_awardings_of_badge(badge.id)

    assert actual == set()


def test_get_awardings_of_badge(
    party_app, user1, user2, badge1, awardings_scope
):
    badge = badge1

    badge_command_service.award_badge_to_user(badge.id, user1.id)
    badge_command_service.award_badge_to_user(badge.id, user1.id)
    badge_command_service.award_badge_to_user(badge.id, user2.id)

    actual = badge_service.get_awardings_of_badge(badge.id)

    assert actual == {
        QuantifiedBadgeAwarding(badge.id, user1.id, 2),
        QuantifiedBadgeAwarding(badge.id, user2.id, 1),
    }


def _create_badge(slug, label):
    return badge_command_service.create_badge(slug, label, f'{slug}.svg')
