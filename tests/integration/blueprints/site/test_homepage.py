"""
:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from tests.helpers import http_client


def test_homepage(site_app):
    with http_client(site_app) as client:
        response = client.get('http://www.acmecon.test/')

    # no redirect
    assert response.status_code == 200
    assert response.location is None
