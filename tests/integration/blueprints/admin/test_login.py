"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authentication.session import service as session_service
from byceps.services.user import event_service


@pytest.fixture
def client(admin_app, site):
    return admin_app.test_client()


def test_login_form(client):
    response = client.get('/authentication/login')

    assert response.status_code == 200


def test_login_succeeds(client, make_admin):
    screen_name = 'AdminLoginTester'
    password = 'correct horse battery staple'
    permission_ids = {'admin.access'}

    user = make_admin(screen_name, permission_ids, password=password)

    login_events_before = event_service.get_events_of_type_for_user(user.id, 'user-logged-in')
    assert len(login_events_before) == 0

    assert session_service.find_recent_login(user.id) is None

    assert not list(client.cookie_jar)

    form_data = {
        'screen_name': screen_name,
        'password': password,
    }

    response = client.post('/authentication/login', data=form_data)
    assert response.status_code == 204
    assert response.location is None

    login_events_after = event_service.get_events_of_type_for_user(user.id, 'user-logged-in')
    assert len(login_events_after) == 1
    login_event = login_events_after[0]
    assert login_event.data == {'ip_address': '127.0.0.1'}

    assert session_service.find_recent_login(user.id) is not None

    cookies = list(client.cookie_jar)
    assert len(cookies) == 1

    cookie = cookies[0]
    assert cookie.domain == '.admin.acmecon.test'
    assert cookie.name == 'session'
    assert cookie.secure


def test_login_fails_lacking_access_permission(client, make_admin):
    screen_name = 'AdminWithoutAccess'
    password = 'correct horse battery staple'
    permission_ids = set()

    user = make_admin(screen_name, permission_ids, password=password)

    assert not list(client.cookie_jar)

    form_data = {
        'screen_name': screen_name,
        'password': password,
    }

    response = client.post('/authentication/login', data=form_data)
    assert response.status_code == 403


def test_login_fails(client):
    form_data = {
        'screen_name': 'TotallyUnknownAdmin',
        'password': 'TotallyWrongPassword',
    }

    response = client.post('/authentication/login', data=form_data)
    assert response.status_code == 401
