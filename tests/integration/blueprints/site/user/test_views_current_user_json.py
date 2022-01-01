"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from tests.helpers import http_client, log_in_user


CONTENT_TYPE_JSON = 'application/json'


def test_when_logged_in(site_app, site, user):
    log_in_user(user.id)

    response = send_request(site_app, user_id=user.id)

    assert response.status_code == 200
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON

    response_data = response.json
    assert response_data['id'] == str(user.id)
    assert response_data['screen_name'] == user.screen_name
    assert response_data['avatar_url'] is None


def test_when_not_logged_in(site_app, site):
    response = send_request(site_app)

    assert response.status_code == 401
    assert response.get_data() == b''


# helpers


def send_request(app, user_id=None):
    url = '/users/me.json'
    with http_client(app, user_id=user_id) as client:
        return client.get(url)
