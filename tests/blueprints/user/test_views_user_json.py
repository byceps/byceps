"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import json

from tests.base import AbstractAppTestCase

from testfixtures.user import create_user


CONTENT_TYPE_JSON = 'application/json'


class UserJsonTestCase(AbstractAppTestCase):

    def test_with_existent_user(self):
        screen_name = 'Gemüsefrau'

        user_id = self.create_user(screen_name)

        response = self.send_request(user_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, CONTENT_TYPE_JSON)
        self.assertEqual(response.mimetype, CONTENT_TYPE_JSON)

        response_data = decode_json_response(response)
        self.assertEqual(response_data['id'], user_id)
        self.assertEqual(response_data['screen_name'], screen_name)

    def test_with_deleted_user(self):
        screen_name = 'DeletedUser'

        user_id = self.create_user(screen_name, deleted=True)

        response = self.send_request(user_id)

        self.assertEqual(response.status_code, 410)
        self.assertEqual(response.content_type, CONTENT_TYPE_JSON)
        self.assertEqual(response.mimetype, CONTENT_TYPE_JSON)

        response_data = decode_json_response(response)
        self.assertDictEqual(response_data, {})

    def test_with_nonexistent_user(self):
        unknown_user_id = '00000000-0000-0000-0000-000000000000'

        response = self.send_request(unknown_user_id)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, CONTENT_TYPE_JSON)
        self.assertEqual(response.mimetype, CONTENT_TYPE_JSON)

        response_data = decode_json_response(response)
        self.assertDictEqual(response_data, {})

    # helpers

    def create_user(self, screen_name, *, deleted=False):
        user = create_user(screen_name)
        user.deleted = deleted

        self.db.session.add(user)
        self.db.session.commit()

        return str(user.id)

    def send_request(self, user_id):
        url = '/users/{}.json'.format(user_id)
        with self.client() as client:
            return client.get(url)


def decode_json_response(response):
    return json.loads(response.get_data(as_text=True))
