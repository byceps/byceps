"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.site import service as site_service

from tests.helpers import create_site, http_client


@pytest.fixture(scope='module')
def site(party_app, make_email_config):
    make_email_config()
    site = create_site()
    yield site
    site_service.delete_site(site.id)


def test_view_profile_of_existing_user(party_app, site, user):
    response = request_profile(party_app, user.id)

    assert response.status_code == 200
    assert response.mimetype == 'text/html'


def test_view_profile_of_uninitialized_user(
    party_app, site, uninitialized_user
):
    response = request_profile(party_app, uninitialized_user.id)

    assert response.status_code == 404


def test_view_profile_of_suspended_user(party_app, site, suspended_user):
    response = request_profile(party_app, suspended_user.id)

    assert response.status_code == 404


def test_view_profile_of_deleted_user(party_app, site, deleted_user):
    response = request_profile(party_app, deleted_user.id)

    assert response.status_code == 404


def test_view_profile_of_unknown_user(party_app, site):
    unknown_user_id = '00000000-0000-0000-0000-000000000000'

    response = request_profile(party_app, unknown_user_id)

    assert response.status_code == 404


# helpers


def request_profile(app, user_id):
    url = f'/users/{user_id}'

    with http_client(app) as client:
        return client.get(url)
