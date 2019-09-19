"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from tests.base import AbstractAppTestCase
from tests.helpers import create_email_config, create_site, create_user, \
    http_client

from ....conftest import database_recreated


CONTENT_TYPE_JSON = 'application/json'


@pytest.fixture(scope='module')
def client(party_app, db):
    app = party_app
    with app.app_context():
        with database_recreated(db):
            create_email_config()
            create_site()

            yield app.test_client()


def test_with_existent_user(client):
    screen_name = 'Gemüsefrau'

    user = create_user(screen_name)
    user_id = str(user.id)

    response = send_request(client, user_id)

    assert response.status_code == 200
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON

    response_data = response.json
    assert response_data['id'] == user_id
    assert response_data['screen_name'] == screen_name
    assert response_data['avatar_url'] is None


def test_with_not_uninitialized_user(client):
    screen_name = 'UninitializedUser'

    user = create_user(screen_name, initialized=False)

    response = send_request(client, str(user.id))

    assert response.status_code == 404
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON
    assert response.json == {}


def test_with_disabled_user(client):
    screen_name = 'DisabledUser'

    user = create_user(screen_name, enabled=False)

    response = send_request(client, str(user.id))

    assert response.status_code == 404
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON
    assert response.json == {}


def test_with_suspended_user(client, db):
    screen_name = 'SuspendedUser'

    user = create_user(screen_name)
    user.suspended = True
    db.session.commit()

    response = send_request(client, str(user.id))

    assert response.status_code == 404
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON
    assert response.json == {}


def test_with_deleted_user(client, db):
    screen_name = 'DeletedUser'

    user = create_user(screen_name)
    user.deleted = True
    db.session.commit()

    response = send_request(client, str(user.id))

    assert response.status_code == 404
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON
    assert response.json == {}


def test_with_nonexistent_user(client):
    unknown_user_id = '00000000-0000-0000-0000-000000000000'

    response = send_request(client, unknown_user_id)

    assert response.status_code == 404
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON
    assert response.json == {}


def send_request(client, user_id):
    return client.get(f'/api/users/{user_id}/profile')
