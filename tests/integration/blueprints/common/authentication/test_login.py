"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authentication.password import service as password_service


@pytest.fixture
def client(site_app, site):
    return site_app.test_client()


def test_login_form(client):
    response = client.get('/authentication/login')

    assert response.status_code == 200


def test_login_succeeds(client, make_user):
    screen_name = 'LoginTester'
    password = 'correct horse battery staple'

    user = make_user(screen_name)
    password_service.create_password_hash(user.id, password)

    assert not list(client.cookie_jar)

    form_data = {
        'screen_name': screen_name,
        'password': password,
    }

    response = client.post('/authentication/login', data=form_data)
    assert response.status_code == 204

    cookies = list(client.cookie_jar)
    assert len(cookies) == 1

    cookie = cookies[0]
    assert cookie.domain == '.www.acmecon.test'
    assert cookie.name == 'session'
    assert cookie.secure


def test_login_fails(client):
    form_data = {
        'screen_name': 'TotallyUnknownUser',
        'password': 'TotallyWrongPassword',
    }

    response = client.post('/authentication/login', data=form_data)
    assert response.status_code == 403
