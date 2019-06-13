"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.tourney.models.match import MatchComment
from byceps.services.tourney import match_service

from tests.base import AbstractAppTestCase
from tests.helpers import create_user


class MatchCommentCreateTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

    def test_create_comment_on_existent_match(self):
        player = self.create_player()

        match_id = self.create_match()

        response = self.request_comment_creation(match_id, user_id=player.id)

        assert response.status_code == 201

        assert get_comment_count_for_match(match_id) == 1

    def test_create_comment_on_existent_match_as_anonymous_user(self):
        match_id = self.create_match()

        response = self.request_comment_creation(match_id)

        assert response.status_code == 403

        assert get_comment_count_for_match(match_id) == 0

    def test_create_comment_on_nonexistent_match(self):
        player = self.create_player()

        unknown_match_id = '00000000-0000-0000-0000-000000000000'

        response = self.request_comment_creation(unknown_match_id,
                                                 user_id=player.id)

        assert response.status_code == 404

    # helpers

    def create_player(self):
        player = create_user()

        self.create_session_token(player.id)

        return player

    def create_match(self):
        return match_service.create_match()

    def request_comment_creation(self, match_id, *, user_id=None):
        url = '/tourney/matches/{}/comments'.format(match_id)

        form_data = {
            'body': 'gg',
        }

        with self.client(user_id=user_id) as client:
            return client.post(url, data=form_data)


def get_comment_count_for_match(match_id):
    return MatchComment.query.for_match(match_id).count()
