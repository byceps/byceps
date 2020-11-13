"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from tests.helpers import login_user


def test_view_for_brand(admin_client, brand):
    url = f'/admin/attendance/brands/{brand.id}'
    response = admin_client.get(url)
    assert response.status_code == 200


@pytest.fixture(scope='package')
def admin(make_admin):
    permission_ids = {'admin.access'}
    admin = make_admin('AttendanceAdmin', permission_ids)
    login_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def admin_client(make_client, admin_app, admin):
    return make_client(admin_app, user_id=admin.id)
