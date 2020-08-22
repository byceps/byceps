"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from unittest.mock import patch


# Test against an admin app because that doesn't require setup of brand
# party. After all, both admin and party apps should react the same.


@patch('byceps.blueprints.monitoring.healthcheck.views._is_rdbms_ok')
def test_healthcheck_fail(is_rdbms_ok_mock, admin_client):
    expected_media_type = 'application/health+json'

    is_rdbms_ok_mock.return_value = False

    response = admin_client.get('/health')

    assert response.status_code == 503
    assert response.content_type == expected_media_type
    assert response.mimetype == expected_media_type
    assert response.get_json() == {
        'status': 'ok',
        'details': {
            'rdbms': [{'status': 'fail'}],
        },
    }
