"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.authentication.session import authn_session_service
from byceps.services.user import user_log_service


@pytest.fixture()
def client(admin_app, site):
    return admin_app.test_client()


def test_login_form(client):
    response = client.get('/authentication/log_in')

    assert response.status_code == 200


def test_login_succeeds(client, make_admin):
    password = 'correct horse battery staple'
    permission_ids = {'admin.access'}

    user = make_admin(permission_ids, password=password)

    login_log_entries_before = user_log_service.get_entries_of_type_for_user(
        user.id, 'user-logged-in'
    )
    assert len(login_log_entries_before) == 0

    assert authn_session_service.find_recent_login(user.id) is None

    assert get_session_cookie(client) is None

    form_data = {
        'username': user.screen_name,
        'password': password,
    }

    response = client.post('/authentication/log_in', data=form_data)
    assert response.status_code == 302
    assert response.location == '/'

    login_log_entries_after = user_log_service.get_entries_of_type_for_user(
        user.id, 'user-logged-in'
    )
    assert len(login_log_entries_after) == 1
    login_log_entry = login_log_entries_after[0]
    assert login_log_entry.data == {'ip_address': '127.0.0.1'}

    assert authn_session_service.find_recent_login(user.id) is not None

    cookie = get_session_cookie(client)
    assert cookie is not None
    assert cookie.secure


def test_login_fails_with_invalid_credentials(client):
    form_data = {
        'username': 'TotallyUnknownAdmin',
        'password': 'TotallyWrongPassword',
    }

    response = client.post('/authentication/log_in', data=form_data)
    assert response.status_code == 200

    assert get_session_cookie(client) is None


def test_login_fails_lacking_access_permission(client, make_user):
    password = 'correct horse battery staple'

    user = make_user(password=password)

    assert get_session_cookie(client) is None

    form_data = {
        'username': user.screen_name,
        'password': password,
    }

    response = client.post('/authentication/log_in', data=form_data)
    assert response.status_code == 200

    assert get_session_cookie(client) is None


def get_session_cookie(client):
    return client.get_cookie('session', domain='admin.acmecon.test')
