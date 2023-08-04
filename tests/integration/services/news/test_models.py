"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.news import news_item_service
from byceps.services.news.models import BodyFormat, NewsChannel, NewsItem

from tests.helpers import generate_token


@pytest.fixture(scope='module')
def editor(make_user):
    return make_user()


@pytest.fixture(scope='module')
def brand(make_brand):
    return make_brand()


@pytest.fixture()
def channel(brand, make_news_channel) -> NewsChannel:
    return make_news_channel(brand)


@pytest.fixture()
def news_item_with_image(channel: NewsChannel, editor) -> NewsItem:
    return create_item(channel.id, editor.id, image_url_path='breaking.png')


@pytest.fixture()
def news_item_without_image(channel: NewsChannel, editor) -> NewsItem:
    return create_item(channel.id, editor.id)


def test_image_url_with_image(news_item_with_image):
    channel = news_item_with_image.channel

    assert (
        news_item_with_image.image_url_path
        == f'/data/global/news_channels/{channel.id}/breaking.png'
    )


def test_image_url_without_image(news_item_without_image):
    assert news_item_without_image.image_url_path is None


# helpers


def create_item(channel_id, editor_id, *, image_url_path=None) -> NewsItem:
    slug = generate_token()
    title = 'the title'
    body = 'the body'
    body_format = BodyFormat.html

    item = news_item_service.create_item(
        channel_id,
        slug,
        editor_id,
        title,
        body,
        body_format,
        image_url_path=image_url_path,
    )

    return news_item_service.find_item(item.id)
