"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.news import (
    channel_service as news_channel_service,
    service as news_service,
)

from tests.helpers import create_brand, create_user

from ...conftest import database_recreated


def test_image_url_with_image(app):
    item = create_item(
        app.channel.id,
        'with-image',
        app.editor.id,
        image_url_path='breaking.png',
    )

    assert item.image_url == 'http://example.com/brand/news/breaking.png'


def test_image_url_without_image(app):
    item = create_item(app.channel.id, 'without-image', app.editor.id)

    assert item.image_url is None


@pytest.fixture(scope='module')
def app(party_app, db):
    with party_app.app_context():
        with database_recreated(db):
            _app = party_app

            brand = create_brand()

            _app.channel = create_channel(brand.id)

            _app.editor = create_user('Editor')

            yield _app


def create_channel(brand_id):
    channel_id = '{}-test'.format(brand_id)
    url_prefix = 'https://example.com/news/'
    return news_channel_service.create_channel(brand_id, channel_id, url_prefix)


def create_item(channel_id, slug, editor_id, *, image_url_path=None):
    title = 'the title'
    body = 'the body'

    item = news_service.create_item(
        channel_id, slug, editor_id, title, body, image_url_path=image_url_path
    )

    # Return aggregated version of item.
    return news_service.find_aggregated_item_by_slug(channel_id, slug)
