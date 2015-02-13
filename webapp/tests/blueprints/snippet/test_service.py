# -*- coding: utf-8 -*-

from datetime import datetime

from byceps.blueprints.snippet.service import find_latest_version_of_snippet, \
    SnippetNotFound

from testfixtures.party import create_party
from testfixtures.snippet import create_snippet, create_snippet_version
from testfixtures.user import create_user
from tests import AbstractAppTestCase
from tests.helpers import current_party_set


class FindLatestVersionOfSnippetTestCase(AbstractAppTestCase):

    def setUp(self):
        super(FindLatestVersionOfSnippetTestCase, self).setUp()

        self.party2014 = self.create_party('lafiesta-2014', 4, 'La Fiesta 2014')
        self.party2015 = self.create_party('lafiesta-2015', 5, 'La Fiesta 2015')

        self.snippet_creator = create_user(1)
        self.db.session.add(self.snippet_creator)

        self.db.session.commit()

    def test_current_party_is_considered(self):
        snippet_info2014_version = self.create_snippet_with_version(self.party2014, 'info', '2014-10-23 14:55:00')
        snippet_info2015_version = self.create_snippet_with_version(self.party2015, 'info', '2014-10-23 18:21:00')
        self.db.session.commit()

        with current_party_set(self.app, self.party2014), self.app.app_context():
            actual = find_latest_version_of_snippet('info')
            self.assertEquals(actual, snippet_info2014_version)

    def test_unknown_name(self):
        with current_party_set(self.app, self.party2014), self.app.app_context():
            with self.assertRaises(SnippetNotFound):
                find_latest_version_of_snippet('totally-unknown-snippet-name')

    # -------------------------------------------------------------------- #
    # helpers

    def create_party(self, id, number, title):
        party = create_party(id=id, number=number, title=title, brand=self.brand)
        self.db.session.add(party)
        return party

    def create_snippet_with_version(self, party, name, created_at_text):
        snippet = create_snippet(party, name)
        self.db.session.add(snippet)

        created_at = datetime.strptime(created_at_text, '%Y-%m-%d %H:%M:%S')
        version = create_snippet_version(snippet, self.snippet_creator, created_at=created_at)
        self.db.session.add(version)

        return version
