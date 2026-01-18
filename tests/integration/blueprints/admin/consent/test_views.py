"""
:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

BASE_URL = 'http://admin.acmecon.test'


def test_index(consent_admin_client):
    url = f'{BASE_URL}/consent/subjects'
    response = consent_admin_client.get(url)
    assert response.status_code == 200
