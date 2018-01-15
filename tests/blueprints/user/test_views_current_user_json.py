"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import json

from tests.base import AbstractAppTestCase


CONTENT_TYPE_JSON = 'application/json'


class CurrentUserJsonTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.user = self.create_user('McFly')
        self.create_session_token(self.user.id)

        self.create_brand_and_party()

    def test_when_logged_in(self):
        response = self.send_request(user=self.user)

        assert response.status_code == 200
        assert response.content_type == CONTENT_TYPE_JSON
        assert response.mimetype == CONTENT_TYPE_JSON

        response_data = decode_json_response(response)
        assert response_data['id'] == str(self.user.id)
        assert response_data['screen_name'] == self.user.screen_name

    def test_when_not_logged_in(self):
        response = self.send_request()

        assert response.status_code == 404
        assert response.content_type == CONTENT_TYPE_JSON
        assert response.mimetype == CONTENT_TYPE_JSON

        response_data = decode_json_response(response)
        assert response_data == {}

    # helpers

    def send_request(self, *, user=None):
        url = '/users/me.json'
        with self.client(user=user) as client:
            return client.get(url)


def decode_json_response(response):
    return json.loads(response.get_data(as_text=True))
