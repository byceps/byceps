"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from tests.conftest import database_recreated
from tests.helpers import create_site, http_client, login_user


@pytest.fixture(scope='module')
def app(party_app, db, make_email_config):
    with party_app.app_context():
        with database_recreated(db):
            make_email_config()
            create_site()
            yield party_app


def test_when_logged_in_form_is_available(app, user):
    login_user(user.id)

    response = send_request(app, user_id=user.id)

    assert response.status_code == 200


def test_when_not_logged_in_form_is_unavailable(app):
    response = send_request(app)

    assert response.status_code == 404


# helpers


def send_request(app, user_id=None):
    url = '/authentication/password/update'
    with http_client(app, user_id=user_id) as client:
        return client.get(url)
