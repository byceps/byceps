"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from tests.helpers import log_in_user


def test_view_for_brand(jobs_admin_client):
    url = '/admin/jobs/'
    response = jobs_admin_client.get(url)
    assert response.status_code == 200


@pytest.fixture(scope='package')
def jobs_admin(make_admin):
    permission_ids = {
        'admin.access',
        'jobs.view',
    }
    admin = make_admin('JobsAdmin', permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def jobs_admin_client(make_client, admin_app, jobs_admin):
    return make_client(admin_app, user_id=jobs_admin.id)
