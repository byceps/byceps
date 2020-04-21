"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.site import service as site_service

from tests.helpers import create_site, http_client, login_user


@pytest.fixture(scope='module')
def site(party_app_with_db, make_email_config):
    make_email_config()
    site = create_site()
    yield site
    site_service.delete_site(site.id)


def test_when_logged_in_form_is_available(party_app_with_db, site, user):
    login_user(user.id)

    response = send_request(party_app_with_db, user_id=user.id)

    assert response.status_code == 200


def test_when_not_logged_in_form_is_unavailable(party_app_with_db, site):
    response = send_request(party_app_with_db)

    assert response.status_code == 404


# helpers


def send_request(app, user_id=None):
    url = '/authentication/password/update'
    with http_client(app, user_id=user_id) as client:
        return client.get(url)
