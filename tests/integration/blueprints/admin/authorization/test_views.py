"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.helpers import http_client


def test_permission_index(admin_app, role_admin, permission):
    url = '/admin/authorization/permissions'
    response = get_resource(admin_app, role_admin, url)
    assert response.status_code == 200


def test_role_index(admin_app, role_admin, role):
    url = '/admin/authorization/roles'
    response = get_resource(admin_app, role_admin, url)
    assert response.status_code == 200


def test_role_view(admin_app, role_admin, role):
    url = f'/admin/authorization/roles/{role.id}'
    response = get_resource(admin_app, role_admin, url)
    assert response.status_code == 200


# helpers


def get_resource(app, user, url):
    with http_client(app, user_id=user.id) as client:
        return client.get(url)
