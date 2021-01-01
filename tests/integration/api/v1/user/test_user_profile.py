"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

CONTENT_TYPE_JSON = 'application/json'


def test_with_existent_user(api_client, user):
    response = send_request(api_client, user.id)

    assert response.status_code == 200
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON

    response_data = response.json
    assert response_data['id'] == str(user.id)
    assert response_data['screen_name'] == 'User'
    assert response_data['avatar_url'] is None


def test_with_not_uninitialized_user(api_client, uninitialized_user):
    user = uninitialized_user

    response = send_request(api_client, str(user.id))

    assert response.status_code == 404
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON
    assert response.json == {}


def test_with_suspended_user(api_client, suspended_user):
    user = suspended_user

    response = send_request(api_client, str(user.id))

    assert response.status_code == 404
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON
    assert response.json == {}


def test_with_deleted_user(api_client, deleted_user):
    user = deleted_user

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
    return api_client.get(f'/api/v1/users/{user_id}/profile')
