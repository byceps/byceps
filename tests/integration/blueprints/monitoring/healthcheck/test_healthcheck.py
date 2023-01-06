"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from unittest.mock import patch

import pytest


# Test against an admin app because that doesn't require setup of brand
# party. After all, both admin and party apps should react the same.


def test_healthcheck_ok(client):
    expected_media_type = 'application/health+json'

    response = client.get('/health')

    assert response.status_code == 200
    assert response.content_type == expected_media_type
    assert response.mimetype == expected_media_type
    assert response.get_json() == {
        'status': 'ok',
        'details': {
            'rdbms': [{'status': 'ok'}],
        },
    }


@patch('byceps.blueprints.monitoring.healthcheck.views._is_rdbms_ok')
def test_healthcheck_fail(is_rdbms_ok_mock, client):
    expected_media_type = 'application/health+json'

    is_rdbms_ok_mock.return_value = False

    response = client.get('/health')

    assert response.status_code == 503
    assert response.content_type == expected_media_type
    assert response.mimetype == expected_media_type
    assert response.get_json() == {
        'status': 'ok',
        'details': {
            'rdbms': [{'status': 'fail'}],
        },
    }


@pytest.fixture(scope='module')
def client(make_client, admin_app):
    return make_client(admin_app)
