"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from tests.helpers import http_client


def test_homepage(party_app_with_db, site):
    with http_client(party_app_with_db) as client:
        response = client.get('/')

    # By default, nothing is mounted on `/`, but at least check that
    # the application boots up and doesn't return a server error.
    assert response.status_code == 404
