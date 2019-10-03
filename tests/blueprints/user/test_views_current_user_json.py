"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.base import AbstractAppTestCase
from tests.helpers import (
    create_email_config,
    create_site,
    create_user,
    http_client,
    login_user,
)


CONTENT_TYPE_JSON = 'application/json'


class CurrentUserJsonTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        create_email_config()
        create_site()

    def test_when_logged_in(self):
        user = create_user('McFly')
        login_user(user.id)

        response = self.send_request(user_id=user.id)

        assert response.status_code == 200
        assert response.content_type == CONTENT_TYPE_JSON
        assert response.mimetype == CONTENT_TYPE_JSON

        response_data = response.json
        assert response_data['id'] == str(user.id)
        assert response_data['screen_name'] == user.screen_name
        assert response_data['avatar_url'] is None

    def test_when_not_logged_in(self):
        response = self.send_request()

        assert response.status_code == 403
        assert response.get_data() == b''

    # helpers

    def send_request(self, *, user_id=None):
        url = '/users/me.json'
        with http_client(self.app, user_id=user_id) as client:
            return client.get(url)
