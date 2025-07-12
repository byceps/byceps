"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest
from sqlalchemy import delete

from byceps.database import db
from byceps.services.user_badge import (
    user_badge_awarding_service,
    user_badge_service,
)
from byceps.services.user_badge.dbmodels import DbBadgeAwarding
from byceps.services.user_badge.models import QuantifiedBadgeAwarding


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


def test_count_awardings(
    database,
    user1,
    user2,
    user3,
    badge1,
    badge2,
    badge3,
    awardings_scope,
):
    user_badge_awarding_service.award_badge_to_user(badge1, user1)
    user_badge_awarding_service.award_badge_to_user(badge1, user1)
    user_badge_awarding_service.award_badge_to_user(badge1, user2)
    user_badge_awarding_service.award_badge_to_user(badge1, user3)
    user_badge_awarding_service.award_badge_to_user(badge3, user2)
    user_badge_awarding_service.award_badge_to_user(badge3, user3)

    actual = user_badge_awarding_service.count_awardings()

    # Remove counts for potential other badges.
    relevant_badge_ids = {badge1.id, badge2.id, badge3.id}
    actual_relevant = {
        k: v for k, v in actual.items() if k in relevant_badge_ids
    }

    assert actual_relevant == {badge1.id: 4, badge2.id: 0, badge3.id: 2}


def test_get_awardings_of_unknown_badge(database):
    unknown_badge_id = '00000000-0000-0000-0000-000000000000'

    actual = user_badge_awarding_service.get_awardings_of_badge(
        unknown_badge_id
    )

    assert actual == set()


def test_get_awardings_of_unawarded_badge(database, badge3):
    badge = badge3

    actual = user_badge_awarding_service.get_awardings_of_badge(badge.id)

    assert actual == set()


def test_get_awardings_of_badge(
    database, user1, user2, badge1, awardings_scope
):
    badge = badge1

    user_badge_awarding_service.award_badge_to_user(badge, user1)
    user_badge_awarding_service.award_badge_to_user(badge, user1)
    user_badge_awarding_service.award_badge_to_user(badge, user2)

    actual = user_badge_awarding_service.get_awardings_of_badge(badge.id)

    assert actual == {
        QuantifiedBadgeAwarding(
            badge_id=badge.id,
            awardee_id=user1.id,
            quantity=2,
        ),
        QuantifiedBadgeAwarding(
            badge_id=badge.id,
            awardee_id=user2.id,
            quantity=1,
        ),
    }


def _create_badge(slug, label):
    return user_badge_service.create_badge(slug, label, f'{slug}.svg')
