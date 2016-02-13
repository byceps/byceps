# -*- coding: utf-8 -*-

"""
:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.blueprints.tourney.models.match import MatchComment

from testfixtures.tourney import create_match
from testfixtures.user import create_user

from tests.base import AbstractAppTestCase


class MatchTestCase(AbstractAppTestCase):

    def test_create_comment_on_existent_match(self):
        player = self.create_player()

        match = self.create_match()

        url = '/tourney/matches/{}/comments'.format(match.id)

        form_data = {
            'body': 'gg',
        }

        with self.client(user=player) as client:
            response = client.post(url, data=form_data)

        self.assertEqual(response.status_code, 201)

        comment_count = MatchComment.query.for_match(match).count()
        self.assertEqual(comment_count, 1)

    def test_create_comment_on_existent_match_as_anonymous_user(self):
        match = self.create_match()

        url = '/tourney/matches/{}/comments'.format(match.id)

        form_data = {
            'body': 'gg',
        }

        with self.client() as client:
            response = client.post(url, data=form_data)

        self.assertEqual(response.status_code, 403)

        comment_count = MatchComment.query.for_match(match).count()
        self.assertEqual(comment_count, 0)

    def test_create_comment_on_nonexistent_match(self):
        player = self.create_player()

        unknown_match_id = '00000000-0000-0000-0000-000000000000'

        url = '/tourney/matches/{}/comments'.format(unknown_match_id)

        form_data = {
            'body': 'gg',
        }

        with self.client(user=player) as client:
            response = client.post(url, data=form_data)

        self.assertEqual(response.status_code, 404)

    # helpers

    def create_player(self):
        player = create_user(27)

        self.db.session.add(player)
        self.db.session.commit()

        return player

    def create_match(self):
        match = create_match()

        self.db.session.add(match)
        self.db.session.commit()

        return match
