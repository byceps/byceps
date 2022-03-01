"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""


def test_view_global(webhook_admin_client):
    url = '/admin/webhooks/'
    response = webhook_admin_client.get(url)
    assert response.status_code == 200
