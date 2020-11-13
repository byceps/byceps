"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from tests.helpers import http_client


def test_view_profile_of_existing_user(site_app, site, user):
    response = request_profile(site_app, user.id)

    assert response.status_code == 200
    assert response.mimetype == 'text/html'


def test_view_profile_of_uninitialized_user(
    site_app, site, uninitialized_user
):
    response = request_profile(site_app, uninitialized_user.id)

    assert response.status_code == 404


def test_view_profile_of_suspended_user(site_app, site, suspended_user):
    response = request_profile(site_app, suspended_user.id)

    assert response.status_code == 404


def test_view_profile_of_deleted_user(site_app, site, deleted_user):
    response = request_profile(site_app, deleted_user.id)

    assert response.status_code == 404


def test_view_profile_of_unknown_user(site_app, site):
    unknown_user_id = '00000000-0000-0000-0000-000000000000'

    response = request_profile(site_app, unknown_user_id)

    assert response.status_code == 404


# helpers


def request_profile(app, user_id):
    url = f'/users/{user_id}'

    with http_client(app) as client:
        return client.get(url)
