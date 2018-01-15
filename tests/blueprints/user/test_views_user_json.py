"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import json

from tests.base import AbstractAppTestCase


CONTENT_TYPE_JSON = 'application/json'


class UserJsonTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.create_brand_and_party()

    def test_with_existent_user(self):
        screen_name = 'Gemüsefrau'

        user = self.create_user(screen_name)
        user_id = str(user.id)

        response = self.send_request(user_id)

        assert response.status_code == 200
        assert response.content_type == CONTENT_TYPE_JSON
        assert response.mimetype == CONTENT_TYPE_JSON

        response_data = decode_json_response(response)
        assert response_data['id'] == user_id
        assert response_data['screen_name'] == screen_name

    def test_with_deleted_user(self):
        screen_name = 'DeletedUser'

        user = self.create_user(screen_name)
        user.deleted = True

        response = self.send_request(str(user.id))

        assert response.status_code == 410
        assert response.content_type == CONTENT_TYPE_JSON
        assert response.mimetype == CONTENT_TYPE_JSON

        response_data = decode_json_response(response)
        assert response_data == {}

    def test_with_nonexistent_user(self):
        unknown_user_id = '00000000-0000-0000-0000-000000000000'

        response = self.send_request(unknown_user_id)

        assert response.status_code == 404
        assert response.content_type == CONTENT_TYPE_JSON
        assert response.mimetype == CONTENT_TYPE_JSON

        response_data = decode_json_response(response)
        assert response_data == {}

    # helpers

    def send_request(self, user_id):
        url = '/users/{}.json'.format(user_id)
        with self.client() as client:
            return client.get(url)


def decode_json_response(response):
    return json.loads(response.get_data(as_text=True))
