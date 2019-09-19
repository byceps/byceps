"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.base import AbstractAppTestCase
from tests.helpers import create_email_config, create_site, create_user, \
    http_client


CONTENT_TYPE_JSON = 'application/json'


class UserJsonTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        create_email_config()
        create_site()

    def test_with_existent_user(self):
        screen_name = 'Gemüsefrau'

        user = create_user(screen_name)
        user_id = str(user.id)

        response = self.send_request(user_id)

        assert response.status_code == 200
        assert response.content_type == CONTENT_TYPE_JSON
        assert response.mimetype == CONTENT_TYPE_JSON

        response_data = response.json
        assert response_data['id'] == user_id
        assert response_data['screen_name'] == screen_name
        assert response_data['avatar_url'] is None

    def test_with_not_uninitialized_user(self):
        screen_name = 'UninitializedUser'

        user = create_user(screen_name, initialized=False)

        response = self.send_request(str(user.id))

        assert response.status_code == 404
        assert response.content_type == CONTENT_TYPE_JSON
        assert response.mimetype == CONTENT_TYPE_JSON
        assert response.json == {}

    def test_with_disabled_user(self):
        screen_name = 'DisabledUser'

        user = create_user(screen_name, enabled=False)

        response = self.send_request(str(user.id))

        assert response.status_code == 404
        assert response.content_type == CONTENT_TYPE_JSON
        assert response.mimetype == CONTENT_TYPE_JSON
        assert response.json == {}

    def test_with_suspended_user(self):
        screen_name = 'SuspendedUser'

        user = create_user(screen_name)
        user.suspended = True
        self.db.session.commit()

        response = self.send_request(str(user.id))

        assert response.status_code == 404
        assert response.content_type == CONTENT_TYPE_JSON
        assert response.mimetype == CONTENT_TYPE_JSON
        assert response.json == {}

    def test_with_deleted_user(self):
        screen_name = 'DeletedUser'

        user = create_user(screen_name)
        user.deleted = True
        self.db.session.commit()

        response = self.send_request(str(user.id))

        assert response.status_code == 404
        assert response.content_type == CONTENT_TYPE_JSON
        assert response.mimetype == CONTENT_TYPE_JSON
        assert response.json == {}

    def test_with_nonexistent_user(self):
        unknown_user_id = '00000000-0000-0000-0000-000000000000'

        response = self.send_request(unknown_user_id)

        assert response.status_code == 404
        assert response.content_type == CONTENT_TYPE_JSON
        assert response.mimetype == CONTENT_TYPE_JSON
        assert response.json == {}

    # helpers

    def send_request(self, user_id):
        url = '/users/{}.json'.format(user_id)
        with http_client(self.app) as client:
            return client.get(url)
