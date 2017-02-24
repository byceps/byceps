"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from nose2.tools import params

from testfixtures.news import create_current_version_association, \
    create_item, create_item_version

from tests.base import AbstractAppTestCase
from tests.helpers import current_party_set


class ItemTestCase(AbstractAppTestCase):

    @params(
        ('without-image', None          , None                                        ),
        ('with-image'   , 'breaking.png', 'http://example.com/brand/news/breaking.png'),
    )
    def test_image_url(self, slug, image_url_path, expected):
        item = self.create_item_with_version(slug, image_url_path)

        with current_party_set(self.app, self.party), self.app.app_context():
            self.assertEqual(item.image_url, expected)

    # -------------------------------------------------------------------- #
    # helpers

    def create_item_with_version(self, slug, image_url_path):
        item = create_item(self.brand.id, slug=slug)
        self.db.session.add(item)

        version = create_item_version(item, self.admin.id,
                                      image_url_path=image_url_path)
        self.db.session.add(version)

        current_version_association = create_current_version_association(item, version)
        self.db.session.add(current_version_association)

        self.db.session.commit()

        return item
