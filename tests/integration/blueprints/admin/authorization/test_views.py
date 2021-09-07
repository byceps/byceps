"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""


def test_permission_index(role_admin_client):
    url = '/admin/authorization/permissions'
    response = role_admin_client.get(url)
    assert response.status_code == 200


def test_role_index(role_admin_client, role):
    url = '/admin/authorization/roles'
    response = role_admin_client.get(url)
    assert response.status_code == 200


def test_role_view(role_admin_client, role):
    url = f'/admin/authorization/roles/{role.id}'
    response = role_admin_client.get(url)
    assert response.status_code == 200
