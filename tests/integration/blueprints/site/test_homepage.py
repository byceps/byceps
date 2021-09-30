"""
:Copyright: 2006-2021 Jochen Kupperschmidt
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
    assert response.location is None


def test_homepage_with_root_redirect(make_site_app, site):
    site_app = make_site_app(SITE_ID=site.id, ROOT_REDIRECT_TARGET='welcome')

    with http_client(site_app) as client:
        response = client.get('/')

    assert response.status_code == 307
    assert response.location == 'http://www.acmecon.test/welcome'
