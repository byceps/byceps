"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authentication.password import service as password_service
from byceps.services.authentication.session import service as session_service
from byceps.services.user import event_service


@pytest.fixture
def client(site_app, site):
    return site_app.test_client()


def test_login_form(client):
    response = client.get('/authentication/login')

    assert response.status_code == 200


def test_login_succeeds(client, make_user):
    screen_name = 'SiteLoginTester'
    password = 'correct horse battery staple'

    user = make_user(screen_name)
    password_service.create_password_hash(user.id, password)

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
    # Location (used by JavaScript redirect) should point to user
    # user dashboard.
    assert response.location == 'http://www.acmecon.test/dashboard'

    login_events_after = event_service.get_events_of_type_for_user(user.id, 'user-logged-in')
    assert len(login_events_after) == 1
    login_event = login_events_after[0]
    assert login_event.data == {'ip_address': '127.0.0.1'}

    assert session_service.find_recent_login(user.id) is not None

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
