"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""


def test_index(user_admin_client):
    url = '/admin/users/'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_view(user_admin_client, user):
    url = f'/admin/users/{user.id}'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_create_account_form(user_admin_client):
    url = '/admin/users/create'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_set_password_form(user_admin_client, user):
    url = f'/admin/users/{user.id}/password'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_suspend_account_form_with_suspended_user(
    user_admin_client, suspended_user
):
    url = f'/admin/users/{suspended_user.id}/suspend'
    response = user_admin_client.get(url)
    assert response.status_code == 302


def test_suspend_account_form_with_unsuspended_user(user_admin_client, user):
    url = f'/admin/users/{user.id}/suspend'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_unsuspend_account_form_with_suspended_user(
    user_admin_client, suspended_user
):
    url = f'/admin/users/{suspended_user.id}/unsuspend'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_unsuspend_account_form_with_unsuspended_user(user_admin_client, user):
    url = f'/admin/users/{user.id}/unsuspend'
    response = user_admin_client.get(url)
    assert response.status_code == 302


def test_delete_account_form_with_user(user_admin_client, user):
    url = f'/admin/users/{user.id}/delete'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_delete_account_form_with_deleted_user(user_admin_client, deleted_user):
    url = f'/admin/users/{deleted_user.id}/delete'
    response = user_admin_client.get(url)
    assert response.status_code == 302


def test_change_email_address_form(user_admin_client, user):
    url = f'/admin/users/{user.id}/change_email_address'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_change_screen_name_form(user_admin_client, user):
    url = f'/admin/users/{user.id}/change_screen_name'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_view_permissions(user_admin_client, user):
    url = f'/admin/users/{user.id}/permissions'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_manage_roles(user_admin_client, user):
    url = f'/admin/users/{user.id}/roles/assignment'
    response = user_admin_client.get(url)
    assert response.status_code == 200


def test_view_events(user_admin_client, user):
    url = f'/admin/users/{user.id}/events'
    response = user_admin_client.get(url)
    assert response.status_code == 200
