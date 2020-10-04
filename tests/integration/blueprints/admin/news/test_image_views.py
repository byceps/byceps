"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""


def test_create_form(news_admin_client, item):
    url = f'/admin/news/for_item/{item.id}/create'
    response = news_admin_client.get(url)
    assert response.status_code == 200
