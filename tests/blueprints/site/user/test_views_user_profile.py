"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.site import service as site_service

from tests.helpers import create_site, http_client


@pytest.fixture(scope='module')
def site(party_app_with_db, make_email_config):
    make_email_config()
    site = create_site()
    yield site
    site_service.delete_site(site.id)


def test_view_profile_of_existing_user(party_app_with_db, site, user):
    response = request_profile(party_app_with_db, user.id)

    assert response.status_code == 200
    assert response.mimetype == 'text/html'


def test_view_profile_of_uninitialized_user(
    party_app_with_db, site, uninitialized_user
):
    response = request_profile(party_app_with_db, uninitialized_user.id)

    assert response.status_code == 404


def test_view_profile_of_suspended_user(
    party_app_with_db, site, suspended_user
):
    response = request_profile(party_app_with_db, suspended_user.id)

    assert response.status_code == 404


def test_view_profile_of_deleted_user(party_app_with_db, site, deleted_user):
    response = request_profile(party_app_with_db, deleted_user.id)

    assert response.status_code == 404


def test_view_profile_of_unknown_user(party_app_with_db, site):
    unknown_user_id = '00000000-0000-0000-0000-000000000000'

    response = request_profile(party_app_with_db, unknown_user_id)

    assert response.status_code == 404


# helpers


def request_profile(app, user_id):
    url = f'/users/{user_id}'

    with http_client(app) as client:
        return client.get(url)
