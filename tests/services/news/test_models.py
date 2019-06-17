"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.news import channel_service as news_channel_service, \
    service as news_service

from tests.base import AbstractAppTestCase
from tests.helpers import create_brand, create_party, create_user, \
    current_party_set


class ItemTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.editor = create_user()

        brand = create_brand()
        self.party = create_party(brand_id=brand.id)

        channel_id = '{}-test'.format(brand.id)
        self.channel = news_channel_service.create_channel(brand.id, channel_id)

    def test_image_url_with_image(self):
        with current_party_set(self.app, self.party), self.app.app_context():
            item = create_item(self.channel.id, 'with-image', self.editor.id,
                               image_url_path='breaking.png')
            assert item.image_url == 'http://example.com/brand/news/breaking.png'

    def test_image_url_without_image(self):
        with current_party_set(self.app, self.party), self.app.app_context():
            item = create_item(self.channel.id, 'without-image', self.editor.id)
            assert item.image_url is None


def create_item(channel_id, slug, editor_id, *, image_url_path=None):
    title = 'the title'
    body = 'the body'

    item = news_service.create_item(channel_id, slug, editor_id, title, body,
                                    image_url_path=image_url_path)

    # Return aggregated version of item.
    return news_service.find_aggregated_item_by_slug(channel_id, slug)
