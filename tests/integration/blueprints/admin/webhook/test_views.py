"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

BASE_URL = 'http://admin.acmecon.test'


def test_view_global(webhook_admin_client):
    url = f'{BASE_URL}/webhooks/'
    response = webhook_admin_client.get(url)
    assert response.status_code == 200
