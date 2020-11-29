"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.news import (
    channel_service as news_channel_service,
    service as news_service,
)
from byceps.services.site import service as site_service

from tests.helpers import create_site, http_client


@pytest.fixture(scope='module')
def editor(make_user):
    return make_user('Journalist')


@pytest.fixture(scope='module')
def news_channel(brand):
    channel_id = f'{brand.id}-public'
    url_prefix = 'https://www.acmecon.test/news/'

    channel = news_channel_service.create_channel(brand.id, channel_id, url_prefix)

    yield channel

    news_channel_service.delete_channel(channel_id)


@pytest.fixture(scope='module')
def unpublished_news_item(news_channel, editor):
    slug = 'top-article'
    title = 'You will not believe this! [WIP]'
    body = 'Well, …'
    item = news_service.create_item(news_channel.id, slug, editor.id, title, body)

    yield item

    news_service.delete_item(item.id)


@pytest.fixture(scope='module')
def published_news_item(news_channel, editor):
    slug = 'first-post'
    title = 'First Post!'
    body = 'Kann losgehen.'
    item = news_service.create_item(news_channel.id, slug, editor.id, title, body)
    news_service.publish_item(item.id)

    yield item

    news_service.delete_item(item.id)


@pytest.fixture(scope='module')
def news_site(news_channel):
    site = create_site(
        'newsflash',
        news_channel.brand_id,
        news_channel_id=news_channel.id,
    )

    yield site

    site_service.delete_site(site.id)


@pytest.fixture(scope='module')
def news_site_app(make_site_app, news_site):
    return make_site_app(SITE_ID=news_site.id)


def test_view_news_frontpage(news_site_app):
    with http_client(news_site_app) as client:
        response = client.get('/news/')

    assert response.status_code == 200


def test_view_single_published_news_item(news_site_app, published_news_item):
    with http_client(news_site_app) as client:
        response = client.get(f'/news/{published_news_item.slug}')

    assert response.status_code == 200


def test_view_single_unpublished_news_item(news_site_app, unpublished_news_item):
    with http_client(news_site_app) as client:
        response = client.get(f'/news/{unpublished_news_item.slug}')

    assert response.status_code == 404
