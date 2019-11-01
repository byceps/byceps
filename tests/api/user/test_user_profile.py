"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.helpers import create_user


CONTENT_TYPE_JSON = 'application/json'


def test_with_existent_user(api_client):
    screen_name = 'Gemüsefrau'

    user = create_user(screen_name)
    user_id = str(user.id)

    response = send_request(api_client, user_id)

    assert response.status_code == 200
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON

    response_data = response.json
    assert response_data['id'] == user_id
    assert response_data['screen_name'] == screen_name
    assert response_data['avatar_url'] is None


def test_with_not_uninitialized_user(api_client):
    screen_name = 'UninitializedUser'

    user = create_user(screen_name, initialized=False)

    response = send_request(api_client, str(user.id))

    assert response.status_code == 404
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON
    assert response.json == {}


def test_with_suspended_user(api_client, db):
    screen_name = 'SuspendedUser'

    user = create_user(screen_name)
    user.suspended = True
    db.session.commit()

    response = send_request(api_client, str(user.id))

    assert response.status_code == 404
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON
    assert response.json == {}


def test_with_deleted_user(api_client, db):
    screen_name = 'DeletedUser'

    user = create_user(screen_name)
    user.deleted = True
    db.session.commit()

    response = send_request(api_client, str(user.id))

    assert response.status_code == 404
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON
    assert response.json == {}


def test_with_nonexistent_user(api_client):
    unknown_user_id = '00000000-0000-0000-0000-000000000000'

    response = send_request(api_client, unknown_user_id)

    assert response.status_code == 404
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON
    assert response.json == {}


def send_request(api_client, user_id):
    return api_client.get(f'/api/users/{user_id}/profile')
