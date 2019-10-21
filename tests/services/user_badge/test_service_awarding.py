"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.user_badge import service as user_badge_service
from byceps.services.user_badge.transfer.models import QuantifiedBadgeAwarding

from ...conftest import database_recreated
from ...helpers import create_user


@pytest.fixture(scope='module')
def app(party_app, db):
    with party_app.app_context():
        with database_recreated(db):
            yield


def test_get_awardings_of_unknown_badge(app):
    unknown_badge_id = '00000000-0000-0000-0000-000000000000'

    actual = user_badge_service.get_awardings_of_badge(unknown_badge_id)

    assert actual == set()


def test_get_awardings_of_unawarded_badge(app):
    badge = user_badge_service.create_badge(
        'awesomeness', 'Certificate of Awesomeness', 'awesomeness.svg'
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
