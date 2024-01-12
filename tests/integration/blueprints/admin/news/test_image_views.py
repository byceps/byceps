"""
:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

BASE_URL = 'http://admin.acmecon.test'


def test_create_form(news_admin_client, item):
    url = f'{BASE_URL}/news/for_item/{item.id}/create'
    response = news_admin_client.get(url)
    assert response.status_code == 200
