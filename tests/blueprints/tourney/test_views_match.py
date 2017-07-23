"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.tourney.models.match import MatchComment

from testfixtures.authentication import create_session_token
from testfixtures.tourney import create_match
from testfixtures.user import create_user

from tests.base import AbstractAppTestCase


class MatchTestCase(AbstractAppTestCase):

    def test_create_comment_on_existent_match(self):
        player = self.create_player()

        match = self.create_match()

        response = self.request_comment_creation(match.id, user=player)

        self.assertEqual(response.status_code, 201)

        self.assertCommentCountForMatch(match, 1)

    def test_create_comment_on_existent_match_as_anonymous_user(self):
        match = self.create_match()

        response = self.request_comment_creation(match.id)

        self.assertEqual(response.status_code, 403)

        self.assertCommentCountForMatch(match, 0)

    def test_create_comment_on_nonexistent_match(self):
        player = self.create_player()

        unknown_match_id = '00000000-0000-0000-0000-000000000000'

        response = self.request_comment_creation(unknown_match_id, user=player)

        self.assertEqual(response.status_code, 404)

    # helpers

    def create_player(self):
        player = create_user()

        self.db.session.add(player)
        self.db.session.commit()

        session_token = create_session_token(player.id)

        self.db.session.add(session_token)
        self.db.session.commit()

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

    def assertCommentCountForMatch(self, match, expected):
        comment_count = MatchComment.query.for_match(match.id).count()
        self.assertEqual(comment_count, expected)
