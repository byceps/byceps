"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from tests.helpers import http_client, log_in_user


def test_when_logged_in(site_app, user):
    log_in_user(user.id)

    response = send_request(site_app, user_id=user.id)

    assert response.status_code == 200
    assert response.mimetype == 'text/html'


def test_when_not_logged_in(site_app):
    response = send_request(site_app)

    assert response.status_code == 302
    assert 'Location' in response.headers


# helpers


def send_request(app, user_id=None):
    url = '/dashboard'
    with http_client(app, user_id=user_id) as client:
        return client.get(url)
