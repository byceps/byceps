"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from tests.conftest import database_recreated
from tests.helpers import create_site, http_client, login_user


CONTENT_TYPE_JSON = 'application/json'


@pytest.fixture(scope='module')
def app(party_app, db, make_email_config):
    with party_app.app_context():
        with database_recreated(db):
            make_email_config()
            create_site()
            yield party_app


def test_when_logged_in(app, normal_user):
    user = normal_user
    login_user(user.id)

    response = send_request(app, user_id=user.id)

    assert response.status_code == 200
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON

    response_data = response.json
    assert response_data['id'] == str(user.id)
    assert response_data['screen_name'] == user.screen_name
    assert response_data['avatar_url'] is None


def test_when_not_logged_in(app):
    response = send_request(app)

    assert response.status_code == 403
    assert response.get_data() == b''


# helpers


def send_request(app, user_id=None):
    url = '/users/me.json'
    with http_client(app, user_id=user_id) as client:
        return client.get(url)
