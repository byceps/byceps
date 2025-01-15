"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

BASE_URL = 'http://admin.acmecon.test'


def test_index(user_admin_client):
    url = f'{BASE_URL}/users/'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_view(user_admin_client, user):
    url = f'{BASE_URL}/users/{user.id}'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_create_account_form(user_admin_client):
    url = f'{BASE_URL}/users/create'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_set_password_form(user_admin_client, user):
    url = f'{BASE_URL}/users/{user.id}/password'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_suspend_account_form_with_suspended_user(
    user_admin_client, suspended_user
):
    url = f'{BASE_URL}/users/{suspended_user.id}/suspend'
    response = user_admin_client.get(url)
    assert response.status_code == 302


def test_suspend_account_form_with_unsuspended_user(user_admin_client, user):
    url = f'{BASE_URL}/users/{user.id}/suspend'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_unsuspend_account_form_with_suspended_user(
    user_admin_client, suspended_user
):
    url = f'{BASE_URL}/users/{suspended_user.id}/unsuspend'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_unsuspend_account_form_with_unsuspended_user(user_admin_client, user):
    url = f'{BASE_URL}/users/{user.id}/unsuspend'
    response = user_admin_client.get(url)
    assert response.status_code == 302


def test_delete_account_form_with_user(user_admin_client, user):
    url = f'{BASE_URL}/users/{user.id}/delete'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_delete_account_form_with_deleted_user(user_admin_client, deleted_user):
    url = f'{BASE_URL}/users/{deleted_user.id}/delete'
    response = user_admin_client.get(url)
    assert response.status_code == 302


def test_change_email_address_form(user_admin_client, user):
    url = f'{BASE_URL}/users/{user.id}/change_email_address'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_change_screen_name_form(user_admin_client, user):
    url = f'{BASE_URL}/users/{user.id}/change_screen_name'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_view_permissions(user_admin_client, user):
    url = f'{BASE_URL}/users/{user.id}/permissions'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_manage_roles(user_admin_client, user):
    url = f'{BASE_URL}/users/{user.id}/roles/assignment'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_view_events(user_admin_client, user):
    url = f'{BASE_URL}/users/{user.id}/events'
    response = user_admin_client.get(url)
    assert response.status_code == 200
