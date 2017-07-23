"""
:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from byceps.services.snippet.service import \
    get_current_version_of_snippet_with_name, SnippetNotFound

from testfixtures.party import create_party
from testfixtures.snippet import create_current_version_association, \
    create_fragment, create_snippet_version
from testfixtures.user import create_user

from tests.base import AbstractAppTestCase


class GetCurrentVersionOfSnippetTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.party2014 = self.create_party('lafiesta-2014', 'La Fiesta 2014')
        self.party2015 = self.create_party('lafiesta-2015', 'La Fiesta 2015')

        self.creator = self.create_creator()

    def test_current_party_is_considered(self):
        fragment_info2014_version = self.create_fragment_with_version(self.party2014, 'info', '2014-10-23 14:55:00')
        fragment_info2015_version = self.create_fragment_with_version(self.party2015, 'info', '2014-10-23 18:21:00')

        actual = get_current_version_of_snippet_with_name(self.party2014.id, 'info')
        self.assertEqual(actual, fragment_info2014_version)

    def test_unknown_name(self):
        with self.assertRaises(SnippetNotFound):
            get_current_version_of_snippet_with_name(self.party2014.id, 'totally-unknown-snippet-name')

    # -------------------------------------------------------------------- #
    # helpers

    def create_party(self, id, title):
        party = create_party(id=id, title=title, brand=self.brand)
        self.db.session.add(party)
        self.db.session.commit()
        return party

    def create_creator(self):
        creator = create_user()
        self.db.session.add(creator)
        self.db.session.commit()
        return creator

    def create_fragment_with_version(self, party, name, created_at_text):
        snippet = create_fragment(party.id, name)
        self.db.session.add(snippet)

        created_at = datetime.strptime(created_at_text, '%Y-%m-%d %H:%M:%S')
        version = create_snippet_version(snippet, self.creator.id, created_at=created_at)
        self.db.session.add(version)

        current_version_association = create_current_version_association(snippet, version)
        self.db.session.add(current_version_association)

        self.db.session.commit()
        return version
