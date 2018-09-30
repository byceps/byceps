"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.news import service as news_service

from tests.base import AbstractAppTestCase
from tests.helpers import current_party_set


class ItemTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.editor = self.create_user()

        self.create_brand_and_party()

    def test_image_url_with_image(self):
        item = self.create_item('with-image', 'breaking.png')

        with current_party_set(self.app, self.party), self.app.app_context():
            assert item.image_url == 'http://example.com/brand/news/breaking.png'

    def test_image_url_without_image(self):
        item = self.create_item('without-image', None)

        with current_party_set(self.app, self.party), self.app.app_context():
            assert item.image_url is None

    # helpers

    def create_item(self, slug, image_url_path):
        return news_service.create_item(self.brand.id, slug, self.editor.id,
                                        'the title', 'the body',
                                        image_url_path=image_url_path)
