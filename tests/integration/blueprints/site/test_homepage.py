"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from tests.helpers import http_client


def test_homepage(site_app, site):
    with http_client(site_app) as client:
        response = client.get('/')

    # By default, nothing is mounted on `/`, but at least check that
    # the application boots up and doesn't return a server error.
    assert response.status_code == 404
