"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.news import channel_service as news_channel_service, \
    service as news_service

from tests.base import AbstractAppTestCase
from tests.helpers import create_user, current_party_set


class ItemTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.editor = create_user()

        self.create_brand_and_party()

        channel_id = '{}-test'.format(self.brand.id)
        self.channel = news_channel_service.create_channel(self.brand.id,
                                                           channel_id)

    def test_image_url_with_image(self):
        with current_party_set(self.app, self.party), self.app.app_context():
            item = self.create_item('with-image', 'breaking.png')
            assert item.image_url == 'http://example.com/brand/news/breaking.png'

    def test_image_url_without_image(self):
        with current_party_set(self.app, self.party), self.app.app_context():
            item = self.create_item('without-image', None)
            assert item.image_url is None

    # helpers

    def create_item(self, slug, image_url_path):
        item = news_service.create_item(self.channel.id, slug, self.editor.id,
                                        'the title', 'the body',
                                        image_url_path=image_url_path)

        # Return aggregated version of item.
        return news_service.find_aggregated_item_by_slug(self.channel.id, slug)
