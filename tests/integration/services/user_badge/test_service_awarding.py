"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest
from sqlalchemy import delete

from byceps.database import db
from byceps.events.user_badge import UserBadgeAwarded
from byceps.services.user import user_log_service
from byceps.services.user_badge import (
    user_badge_awarding_service,
    user_badge_service,
)
from byceps.services.user_badge.dbmodels.awarding import DbBadgeAwarding
from byceps.services.user_badge.models import QuantifiedBadgeAwarding


@pytest.fixture()
def admin_user(make_user):
    return make_user()


@pytest.fixture(scope='module')
def user1(make_user):
    return make_user()


@pytest.fixture(scope='module')
def user2(make_user):
    return make_user()


@pytest.fixture(scope='module')
def user3(make_user):
    return make_user()


@pytest.fixture(scope='module')
def badge1():
    return _create_badge('attendance', 'You were there.')


@pytest.fixture(scope='module')
def badge2():
    return _create_badge('awesomeness', 'Certificate of Awesomeness')


@pytest.fixture(scope='module')
def badge3():
    return _create_badge('eternal-wisdom', 'Eternal Wisdom')


@pytest.fixture()
def awardings_scope():
    yield

    # Remove badge awardings.
    db.session.execute(delete(DbBadgeAwarding))
    db.session.commit()


def test_award_badge_without_initiator(
    site_app, user1, badge1, awardings_scope
):
    user = user1
    badge = badge1

    log_entries_before = user_log_service.get_entries_for_user(user.id)
    assert len(log_entries_before) == 1  # user creation

    _, event = user_badge_awarding_service.award_badge_to_user(
        badge.id, user.id
    )

    assert event.__class__ is UserBadgeAwarded
    assert event.initiator_id is None
    assert event.initiator_screen_name is None
    assert event.user_id == user.id
    assert event.user_screen_name == user.screen_name
    assert event.badge_id == badge.id
    assert event.badge_label == badge.label

    log_entries_after = user_log_service.get_entries_for_user(user.id)
    assert len(log_entries_after) == 2

    user_awarding_log_entry = log_entries_after[1]
    assert user_awarding_log_entry.event_type == 'user-badge-awarded'
    assert user_awarding_log_entry.data == {'badge_id': str(badge.id)}


def test_award_badge_with_initiator(
    site_app, user2, badge2, admin_user, awardings_scope
):
    user = user2

    badge = badge2

    log_entries_before = user_log_service.get_entries_for_user(user.id)
    assert len(log_entries_before) == 1  # user creation

    _, event = user_badge_awarding_service.award_badge_to_user(
        badge.id, user.id, initiator_id=admin_user.id
    )

    assert event.__class__ is UserBadgeAwarded
    assert event.initiator_id == admin_user.id
    assert event.initiator_screen_name == admin_user.screen_name
    assert event.user_id == user.id
    assert event.user_screen_name == user.screen_name
    assert event.badge_id == badge.id
    assert event.badge_label == badge.label

    log_entries_after = user_log_service.get_entries_for_user(user.id)
    assert len(log_entries_after) == 2

    user_awarding_log_entry = log_entries_after[1]
    assert user_awarding_log_entry.event_type == 'user-badge-awarded'
    assert user_awarding_log_entry.data == {
        'badge_id': str(badge.id),
        'initiator_id': str(admin_user.id),
    }


def test_count_awardings(
    site_app,
    user1,
    user2,
    user3,
    badge1,
    badge2,
    badge3,
    awardings_scope,
):
    user_badge_awarding_service.award_badge_to_user(badge1.id, user1.id)
    user_badge_awarding_service.award_badge_to_user(badge1.id, user1.id)
    user_badge_awarding_service.award_badge_to_user(badge1.id, user2.id)
    user_badge_awarding_service.award_badge_to_user(badge1.id, user3.id)
    user_badge_awarding_service.award_badge_to_user(badge3.id, user2.id)
    user_badge_awarding_service.award_badge_to_user(badge3.id, user3.id)

    actual = user_badge_awarding_service.count_awardings()

    # Remove counts for potential other badges.
    relevant_badge_ids = {badge1.id, badge2.id, badge3.id}
    actual_relevant = {
        k: v for k, v in actual.items() if k in relevant_badge_ids
    }

    assert actual_relevant == {badge1.id: 4, badge2.id: 0, badge3.id: 2}


def test_get_awardings_of_unknown_badge(site_app):
    unknown_badge_id = '00000000-0000-0000-0000-000000000000'

    actual = user_badge_awarding_service.get_awardings_of_badge(
        unknown_badge_id
    )

    assert actual == set()


def test_get_awardings_of_unawarded_badge(site_app, badge3):
    badge = badge3

    actual = user_badge_awarding_service.get_awardings_of_badge(badge.id)

    assert actual == set()


def test_get_awardings_of_badge(
    site_app, user1, user2, badge1, awardings_scope
):
    badge = badge1

    user_badge_awarding_service.award_badge_to_user(badge.id, user1.id)
    user_badge_awarding_service.award_badge_to_user(badge.id, user1.id)
    user_badge_awarding_service.award_badge_to_user(badge.id, user2.id)

    actual = user_badge_awarding_service.get_awardings_of_badge(badge.id)

    assert actual == {
        QuantifiedBadgeAwarding(badge.id, user1.id, 2),
        QuantifiedBadgeAwarding(badge.id, user2.id, 1),
    }


def _create_badge(slug, label):
    return user_badge_service.create_badge(slug, label, f'{slug}.svg')
