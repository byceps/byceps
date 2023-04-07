"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""


def test_index(consent_admin_client):
    url = '/admin/consent/subjects'
    response = consent_admin_client.get(url)
    assert response.status_code == 200
