"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from tests.helpers import http_client, log_in_user


def test_homepage_unauthenticated(admin_app):
    with http_client(admin_app) as client:
        response = client.get('/')

    assert response.status_code == 307
    assert response.location == '/authentication/log_in'


def test_homepage_authenticated(admin_app, admin_user):
    log_in_user(admin_user.id)

    with http_client(admin_app, user_id=admin_user.id) as client:
        response = client.get('/')

    assert response.status_code == 307
    assert response.location == '/admin/dashboard'
