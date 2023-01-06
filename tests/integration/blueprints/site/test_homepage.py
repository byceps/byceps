"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from tests.helpers import http_client


def test_homepage(site_app):
    with http_client(site_app) as client:
        response = client.get('/')

    assert response.status_code == 307
    assert response.location == '/news/'
