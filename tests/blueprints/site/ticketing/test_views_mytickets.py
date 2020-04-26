"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from tests.helpers import create_site, http_client, login_user


def test_when_logged_in(party_app, site, user):
    login_user(user.id)

    response = send_request(party_app, user_id=user.id)

    assert response.status_code == 200
    assert response.mimetype == 'text/html'


def test_when_not_logged_in(party_app, site):
    response = send_request(party_app)

    assert response.status_code == 302
    assert 'Location' in response.headers


# helpers


def send_request(app, user_id=None):
    url = '/tickets/mine'
    with http_client(app, user_id=user_id) as client:
        return client.get(url)
