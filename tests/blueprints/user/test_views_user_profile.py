"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from tests.helpers import http_client


def test_view_profile(party_app_with_db, site, normal_user):
    user = normal_user

    url = f'/users/{user.id}'

    with http_client(party_app_with_db) as client:
        response = client.get(url)

    assert response.status_code == 200
    assert response.mimetype == 'text/html'
