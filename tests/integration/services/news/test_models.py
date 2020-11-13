"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.news import (
    channel_service as news_channel_service,
    service as news_service,
)


@pytest.fixture(scope='module')
def editor(make_user):
    return make_user('NewsEditor')


@pytest.fixture(scope='module')
def channel(brand):
    channel_id = f'{brand.id}-test'
    url_prefix = 'https://www.acmecon.test/news/'

    channel = news_channel_service.create_channel(brand.id, channel_id, url_prefix)

    yield channel

    news_channel_service.delete_channel(channel_id)


@pytest.fixture
def news_item_with_image(channel, editor):
    item = create_item(
        channel.id,
        'with-image',
        editor.id,
        image_url_path='breaking.png',
    )

    yield item

    news_service.delete_item(item.id)


@pytest.fixture
def news_item_without_image(channel, editor):
    item = create_item(channel.id, 'without-image', editor.id)

    yield item

    news_service.delete_item(item.id)


def test_image_url_with_image(news_item_with_image):
    assert news_item_with_image.image_url_path == '/data/global/news_channels/acmecon-test/breaking.png'


def test_image_url_without_image(news_item_without_image):
    assert news_item_without_image.image_url_path is None


# helpers


def create_item(channel_id, slug, editor_id, *, image_url_path=None):
    title = 'the title'
    body = 'the body'

    item = news_service.create_item(
        channel_id, slug, editor_id, title, body, image_url_path=image_url_path
    )

    # Return aggregated version of item.
    return news_service.find_aggregated_item_by_slug(channel_id, slug)
