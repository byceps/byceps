"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.site import service as site_service

from tests.conftest import database_recreated
from tests.helpers import create_site, http_client


@pytest.fixture(scope='module')
def app(party_app, db, make_email_config):
    with party_app.app_context():
        with database_recreated(db):
            make_email_config()
            yield party_app


@pytest.fixture(scope='module')
def site(app):
    site = create_site()
    yield site
    site_service.delete_site(site.id)


def test_view_profile_of_existing_user(app, site, user):
    response = request_profile(app, user.id)

    assert response.status_code == 200
    assert response.mimetype == 'text/html'


def test_view_profile_of_uninitialized_user(app, site, uninitialized_user):
    response = request_profile(app, uninitialized_user.id)

    assert response.status_code == 404


def test_view_profile_of_suspended_user(app, site, suspended_user):
    response = request_profile(app, suspended_user.id)

    assert response.status_code == 404


def test_view_profile_of_deleted_user(app, site, deleted_user):
    response = request_profile(app, deleted_user.id)

    assert response.status_code == 404


def test_view_profile_of_unknown_user(app, site):
    unknown_user_id = '00000000-0000-0000-0000-000000000000'

    response = request_profile(app, unknown_user_id)

    assert response.status_code == 404


# helpers


def request_profile(app, user_id):
    url = f'/users/{user_id}'

    with http_client(app) as client:
        return client.get(url)
