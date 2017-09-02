"""
:Copyright: 2006-2017 Jochen Kupperschmidt
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

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, CONTENT_TYPE_JSON)
        self.assertEqual(response.mimetype, CONTENT_TYPE_JSON)

        response_data = decode_json_response(response)
        self.assertEqual(response_data['id'], str(self.user.id))
        self.assertEqual(response_data['screen_name'], self.user.screen_name)

    def test_when_not_logged_in(self):
        response = self.send_request()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, CONTENT_TYPE_JSON)
        self.assertEqual(response.mimetype, CONTENT_TYPE_JSON)

        response_data = decode_json_response(response)
        self.assertDictEqual(response_data, {})

    # helpers

    def send_request(self, *, user=None):
        url = '/users/me.json'
        with self.client(user=user) as client:
            return client.get(url)


def decode_json_response(response):
    return json.loads(response.get_data(as_text=True))
