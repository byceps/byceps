"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.user_badge.models.awarding import QuantifiedBadgeAwardingTuple
from byceps.services.user_badge import service as user_badge_service

from tests.base import AbstractAppTestCase


class UserBadgeAwardingServiceTestCase(AbstractAppTestCase):

    def test_get_awardings_of_unknown_badge(self):
        unknown_badge_id = '00000000-0000-0000-0000-000000000000'

        with self.app.app_context():
            actual = user_badge_service.get_awardings_of_badge(unknown_badge_id)

        assert actual == set()

    def test_get_awardings_of_unawarded_badge(self):
        with self.app.app_context():
            badge = user_badge_service.create_badge(
                'awesomeness', 'Certificate of Awesomeness', 'awesomeness.svg')

            actual = user_badge_service.get_awardings_of_badge(badge.id)

            assert actual == set()

    def test_get_awardings_of_badge(self):
        user1 = self.create_user('User1')
        user2 = self.create_user('User2')

        with self.app.app_context():
            badge = user_badge_service.create_badge(
                'awesomeness', 'Certificate of Awesomeness', 'awesomeness.svg')

            user_badge_service.award_badge_to_user(badge.id, user1.id)
            user_badge_service.award_badge_to_user(badge.id, user1.id)
            user_badge_service.award_badge_to_user(badge.id, user2.id)

            actual = user_badge_service.get_awardings_of_badge(badge.id)

            assert actual == {
                QuantifiedBadgeAwardingTuple(badge.id, user1.id, 2),
                QuantifiedBadgeAwardingTuple(badge.id, user2.id, 1),
            }
