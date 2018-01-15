"""
:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from testfixtures.news import create_current_version_association, \
    create_item, create_item_version

from tests.base import AbstractAppTestCase
from tests.helpers import current_party_set


class ItemTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.editor = self.create_user()

        self.create_brand_and_party()

    def test_image_url_with_image(self):
        item = self.create_item_with_version('with-image', 'breaking.png')

        with current_party_set(self.app, self.party), self.app.app_context():
            assert item.image_url == 'http://example.com/brand/news/breaking.png'

    def test_image_url_without_image(self):
        item = self.create_item_with_version('without-image', None)

        with current_party_set(self.app, self.party), self.app.app_context():
            assert item.image_url is None

    # -------------------------------------------------------------------- #
    # helpers

    def create_item_with_version(self, slug, image_url_path):
        item = create_item(self.brand.id, slug=slug)
        self.db.session.add(item)

        version = create_item_version(item, self.editor.id,
                                      image_url_path=image_url_path)
        self.db.session.add(version)

        current_version_association = create_current_version_association(item, version)
        self.db.session.add(current_version_association)

        self.db.session.commit()

        return item
