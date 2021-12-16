"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from tests.helpers import http_client, log_in_user


def test_when_logged_in_form_is_available(site_app, site, user):
    log_in_user(user.id)

    response = send_request(site_app, user_id=user.id)

    assert response.status_code == 200


def test_when_not_logged_in_form_is_unavailable(site_app, site):
    response = send_request(site_app)

    assert response.status_code == 404


# helpers


def send_request(app, user_id=None):
    url = '/authentication/password/update'
    with http_client(app, user_id=user_id) as client:
        return client.get(url)
