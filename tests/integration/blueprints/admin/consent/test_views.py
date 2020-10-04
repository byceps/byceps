"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""


def test_index(consent_admin_client):
    url = '/admin/consent/'
    response = consent_admin_client.get(url)
    assert response.status_code == 200
