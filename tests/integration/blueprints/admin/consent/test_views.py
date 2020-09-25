"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.helpers import http_client


def test_index(admin_app, consent_admin):
    url = '/admin/consent/'
    response = get_resource(admin_app, consent_admin, url)
    assert response.status_code == 200


# helpers


def get_resource(app, user, url):
    with http_client(app, user_id=user.id) as client:
        return client.get(url)
