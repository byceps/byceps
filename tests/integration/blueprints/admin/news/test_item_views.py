"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.news import service as item_service


def test_view(news_admin_client, item):
    url = f'/admin/news/items/{item.id}'
    response = news_admin_client.get(url)
    assert response.status_code == 200


def test_view_version(news_admin_client, item):
    version = item_service.get_current_item_version(item.id)
    url = f'/admin/news/versions/{version.id}'
    response = news_admin_client.get(url)
    assert response.status_code == 200


def test_list_versions(news_admin_client, item):
    url = f'/admin/news/items/{item.id}/versions'
    response = news_admin_client.get(url)
    assert response.status_code == 200


def test_compare_versions(news_admin_client, item):
    version = item_service.get_current_item_version(item.id)
    url = f'/admin/news/items/{version.id}/compare_to/{version.id}'
    response = news_admin_client.get(url)
    assert response.status_code == 200


def test_create_form(news_admin_client, channel):
    url = f'/admin/news/for_channel/{channel.id}/create'
    response = news_admin_client.get(url)
    assert response.status_code == 200


def test_create(news_admin_client, channel, news_admin):
    slug = 'what-a-blast'
    title = 'Wow, That Party was a Blast!'
    body = 'So many cool memories.'
    image_url_path = 'party-action.jpeg'

    url = f'/admin/news/for_channel/{channel.id}'
    form_data = {
        'slug': slug,
        'title': title,
        'body_format': 'html',
        'body': body,
        'image_url_path': image_url_path,
    }
    response = news_admin_client.post(url, data=form_data)

    location = response.headers['Location']
    item_id = location.rpartition('/')[-1]

    item = item_service.find_item(item_id)
    assert item is not None
    assert item.id is not None
    assert item.channel.id == channel.id
    assert item.slug == slug
    assert item.published_at is None
    assert not item.published
    assert item.title == title
    assert item.body == body
    assert item.external_url == 'https://newssite.example/posts/what-a-blast'
    assert (
        item.image_url_path
        == f'/data/global/news_channels/{channel.id}/party-action.jpeg'
    )
    assert item.images == []


def test_update_form(news_admin_client, item):
    url = f'/admin/news/items/{item.id}/update'
    response = news_admin_client.get(url)
    assert response.status_code == 200


def test_publish_later_form(news_admin_client, item):
    url = f'/admin/news/items/{item.id}/publish_later'
    response = news_admin_client.get(url)
    assert response.status_code == 200


def test_publish_later(news_admin_client, item):
    item_before = item_service.find_item(item.id)
    assert item_before.published_at is None
    assert not item_before.published

    url = f'/admin/news/items/{item.id}/publish_later'
    form_data = {
        'publish_on': '2021-01-23',
        'publish_at': '23:42',
    }
    response = news_admin_client.post(url, data=form_data)
    assert response.status_code == 302

    item_after = item_service.find_item(item.id)
    assert item_after.published_at is not None
    assert item_after.published


def test_publish_now(news_admin_client, item):
    item_before = item_service.find_item(item.id)
    assert item_before.published_at is None
    assert not item_before.published

    url = f'/admin/news/items/{item.id}/publish_now'
    response = news_admin_client.post(url)
    assert response.status_code == 204

    item_after = item_service.find_item(item.id)
    assert item_after.published_at is not None
    assert item_after.published
