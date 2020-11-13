"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from tests.helpers import http_client


URL_PATH = '/style_guide/'


# `admin_app` fixture is required because it sets up the database.
def test_admin_style_guide_in_debug_mode(admin_app, make_admin_app):
    debug_admin_app = make_admin_app(DEBUG=True)
    assert_response_status_code(debug_admin_app, 200)


def test_admin_style_guide_in_nondebug_mode(admin_app):
    assert_response_status_code(admin_app, 404)


def test_site_style_guide_in_debug_mode(make_site_app, site):
    debug_site_app = make_site_app(DEBUG=True)
    assert_response_status_code(debug_site_app, 200)


def test_site_style_guide_in_nondebug_mode(site_app, site):
    assert_response_status_code(site_app, 404)


# helpers


def assert_response_status_code(app, expected_status_code):
    with http_client(app) as client:
        response = client.get(URL_PATH)

    assert response.status_code == expected_status_code
