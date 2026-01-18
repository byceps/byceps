"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from tests.helpers import http_client


def test_attendees_list(site_app, site):
    with http_client(site_app) as client:
        response = client.get('http://www.acmecon.test/attendance/attendees')

    assert response.status_code == 200
