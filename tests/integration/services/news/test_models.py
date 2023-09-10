"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from io import BytesIO

import pytest

from byceps.services.news import news_image_service, news_item_service
from byceps.services.news.models import BodyFormat, NewsChannel, NewsItem
from byceps.services.user.models.user import User

from tests.helpers import generate_token


def test_image_url_without_image(news_item_without_image):
    item = news_item_without_image

    assert item.image_url_path is None


def test_image_url_with_image(news_item_with_image):
    item = news_item_with_image

    expected = f'/data/global/news_channels/{item.channel.id}/breaking.png'

    assert item.image_url_path == expected


def test_image_url_with_featured_image(news_item_with_featured_image):
    item = news_item_with_featured_image

    filename = item.featured_image.filename
    expected = f'/data/global/news_channels/{item.channel.id}/{filename}'

    assert item.featured_image.url_path == expected


# helpers


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
def news_item_without_image(channel: NewsChannel, editor: User) -> NewsItem:
    return create_item(channel.id, editor)


@pytest.fixture()
def news_item_with_image(channel: NewsChannel, editor: User) -> NewsItem:
    return create_item(channel.id, editor, image_url_path='breaking.png')


@pytest.fixture()
def news_item_with_featured_image(
    channel: NewsChannel, editor: User
) -> NewsItem:
    item = create_item(channel.id, editor)

    image_bytes = BytesIO(b'<svg/')
    image = news_image_service.create_image(editor, item, image_bytes).unwrap()

    news_item_service.set_featured_image(item.id, image.id)

    return news_item_service.find_item(item.id)


def create_item(channel_id, editor: User, *, image_url_path=None) -> NewsItem:
    slug = generate_token()
    title = 'the title'
    body = 'the body'
    body_format = BodyFormat.html

    return news_item_service.create_item(
        channel_id,
        slug,
        editor,
        title,
        body,
        body_format,
        image_url_path=image_url_path,
    )
