"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

# Test against an admin app because that doesn't require setup of brand
# party. After all, both admin and party apps should react the same.


def test_healthcheck_ok(admin_client):
    expected_media_type = 'application/health+json'

    response = admin_client.get('/health')

    assert response.status_code == 200
    assert response.content_type == expected_media_type
    assert response.mimetype == expected_media_type
    assert response.get_json() == {
        'status': 'ok',
        'details': {
            'rdbms': [{'status': 'ok'}],
        },
    }
