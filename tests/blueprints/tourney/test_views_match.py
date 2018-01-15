"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.tourney.models.match import MatchComment

from testfixtures.tourney import create_match

from tests.base import AbstractAppTestCase


class MatchTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

    def test_create_comment_on_existent_match(self):
        player = self.create_player()

        match = self.create_match()

        response = self.request_comment_creation(match.id, user=player)

        assert response.status_code == 201

        assert get_comment_count_for_match(match) == 1

    def test_create_comment_on_existent_match_as_anonymous_user(self):
        match = self.create_match()

        response = self.request_comment_creation(match.id)

        assert response.status_code == 403

        assert get_comment_count_for_match(match) == 0

    def test_create_comment_on_nonexistent_match(self):
        player = self.create_player()

        unknown_match_id = '00000000-0000-0000-0000-000000000000'

        response = self.request_comment_creation(unknown_match_id, user=player)

        assert response.status_code == 404

    # helpers

    def create_player(self):
        player = self.create_user()

        self.create_session_token(player.id)

        return player

    def create_match(self):
        match = create_match()

        self.db.session.add(match)
        self.db.session.commit()

        return match

    def request_comment_creation(self, match_id, *, user=None):
        url = '/tourney/matches/{}/comments'.format(match_id)

        form_data = {
            'body': 'gg',
        }

        with self.client(user=user) as client:
            return client.post(url, data=form_data)


def get_comment_count_for_match(match):
    return MatchComment.query.for_match(match.id).count()
