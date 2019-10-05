"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from base64 import b64encode

from byceps.services.tourney.models.match import MatchComment
from byceps.services.tourney import match_service

from tests.base import AbstractAppTestCase
from tests.api_helpers import assemble_authorization_header
from tests.helpers import (
    create_email_config,
    create_site,
    create_user,
    http_client,
    login_user,
)


class MatchCommentCreateTest(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        create_email_config()
        create_site()

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

        response = self.request_comment_creation(
            unknown_match_id, user_id=player.id
        )

        assert response.status_code == 404

    # helpers

    def create_player(self):
        player = create_user()

        login_user(player.id)

        return player

    def create_match(self):
        return match_service.create_match()

    def request_comment_creation(self, match_id, *, user_id=None):
        url = f'/api/tourney/matches/{match_id}/comments'

        headers = [
            assemble_authorization_header('just-say-PLEASE'),
        ]

        form_data = {
            'body': 'gg',
        }

        with http_client(self.app, user_id=user_id) as client:
            return client.post(url, headers=headers, data=form_data)


def get_comment_count_for_match(match_id):
    return MatchComment.query.for_match(match_id).count()
