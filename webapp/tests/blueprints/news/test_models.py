# -*- coding: utf-8 -*-

from byceps.blueprints.news.models import Item

from nose2.tools import params

from testfixtures.snippet import create_current_version_association, \
    create_snippet, create_snippet_version
from tests import AbstractAppTestCase
from tests.helpers import current_party_set


class ItemTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.app.config['SERVER_NAME'] = 'example.com'

    @params(
        (None,                None                                          ),
        ('news/breaking.png', 'http://example.com/content/news/breaking.png'),
    )
    def test_image_url(self, snippet_image_url_path, expected):
        snippet = self.create_snippet_with_version(snippet_image_url_path)
        self.db.session.commit()

        news_item = Item(brand=self.brand, slug='some-slug', snippet=snippet)
        self.db.session.add(news_item)
        self.db.session.commit()

        with current_party_set(self.app, self.party), self.app.app_context():
            self.assertEquals(news_item.image_url, expected)

    # -------------------------------------------------------------------- #
    # helpers

    def create_snippet_with_version(self, image_url_path):
        snippet = create_snippet(self.party, 'a-nice-text-about-something')
        self.db.session.add(snippet)

        version = create_snippet_version(snippet, self.admin,
                                         image_url_path=image_url_path)
        self.db.session.add(version)

        current_version_association = create_current_version_association(snippet, version)
        self.db.session.add(current_version_association)

        return snippet
