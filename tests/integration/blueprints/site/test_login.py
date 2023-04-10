"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authentication.session import authn_session_service
from byceps.services.user import user_log_service


@pytest.fixture
def client(site_app, site):
    return site_app.test_client()


def test_login_form(client):
    response = client.get('/authentication/log_in')

    assert response.status_code == 200


def test_login_succeeds(site, client, make_user):
    password = 'correct horse battery staple'

    user = make_user(password=password)

    login_log_entries_before = user_log_service.get_entries_of_type_for_user(
        user.id, 'user-logged-in'
    )
    assert len(login_log_entries_before) == 0

    assert authn_session_service.find_recent_login(user.id) is None

    assert not list(client.cookie_jar)

    form_data = {
        'username': user.screen_name,
        'password': password,
    }

    response = client.post('/authentication/log_in', data=form_data)
    assert response.status_code == 204
    # Location (used by JavaScript redirect) should point to user
    # user dashboard.
    assert response.location == '/dashboard'

    login_log_entries_after = user_log_service.get_entries_of_type_for_user(
        user.id, 'user-logged-in'
    )
    assert len(login_log_entries_after) == 1
    login_log_entry = login_log_entries_after[0]
    assert login_log_entry.data == {
        'ip_address': '127.0.0.1',
        'site_id': site.id,
    }

    assert authn_session_service.find_recent_login(user.id) is not None

    cookies = list(client.cookie_jar)
    assert len(cookies) == 1

    cookie = cookies[0]
    assert cookie.domain == '.www.acmecon.test'
    assert cookie.name == 'session'
    assert cookie.secure


def test_login_fails_with_invalid_credentials(client):
    form_data = {
        'username': 'TotallyUnknownUser',
        'password': 'TotallyWrongPassword',
    }

    response = client.post('/authentication/log_in', data=form_data)
    assert response.status_code == 403
