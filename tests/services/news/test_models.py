"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.news import channel_service as news_channel_service, \
    service as news_service

from tests.helpers import create_brand, create_party, current_party_set


def test_image_url_with_image(party_app_with_db, party, admin_user):
    channel = create_channel(party.brand_id)
    editor = admin_user

    item = create_item(channel.id, 'with-image', editor.id,
                       image_url_path='breaking.png')

    assert item.image_url == 'http://example.com/brand/news/breaking.png'


def test_image_url_without_image(party_app_with_db, party, admin_user):
    channel = create_channel(party.brand_id)
    editor = admin_user

    item = create_item(channel.id, 'without-image', editor.id)

    assert item.image_url is None


@pytest.fixture
def party():
    brand = create_brand()
    return create_party(brand_id=brand.id)


def create_channel(brand_id):
    channel_id = '{}-test'.format(brand_id)
    return news_channel_service.create_channel(brand_id, channel_id)


def create_item(channel_id, slug, editor_id, *, image_url_path=None):
    title = 'the title'
    body = 'the body'

    item = news_service.create_item(channel_id, slug, editor_id, title, body,
                                    image_url_path=image_url_path)

    # Return aggregated version of item.
    return news_service.find_aggregated_item_by_slug(channel_id, slug)
