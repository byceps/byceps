"""
:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""


def test_index(consent_admin_client):
    url = '/admin/consent/'
    response = consent_admin_client.get(url)
    assert response.status_code == 200
