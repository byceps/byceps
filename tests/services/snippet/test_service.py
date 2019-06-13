"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope

from testfixtures.snippet import create_current_version_association, \
    create_fragment, create_snippet_version

from tests.base import AbstractAppTestCase
from tests.helpers import create_brand, create_party, create_user


class GetCurrentVersionOfSnippetTestCase(AbstractAppTestCase):

    def setUp(self):
        super().setUp()

        self.brand = create_brand('lafiesta', 'La Fiesta')

        party2014 = create_party(self.brand.id, 'lafiesta-2014', 'La Fiesta 2014')
        party2015 = create_party(self.brand.id, 'lafiesta-2015', 'La Fiesta 2015')

        self.scope_site2014 = Scope.for_site(party2014.id)
        self.scope_site2015 = Scope.for_site(party2015.id)

        self.creator = create_user()

    def test_current_party_is_considered(self):
        fragment_info2014_version = self.create_fragment_with_version(
                self.scope_site2014, 'info', '2014-10-23 14:55:00')
        fragment_info2015_version = self.create_fragment_with_version(
                self.scope_site2015, 'info', '2014-10-23 18:21:00')

        actual = snippet_service.find_current_version_of_snippet_with_name(
            self.scope_site2014, 'info')

        assert actual == fragment_info2014_version

    def test_unknown_name(self):
        actual = snippet_service.find_current_version_of_snippet_with_name(
            self.scope_site2014, 'totally-unknown-snippet-name')

        assert actual is None

    # -------------------------------------------------------------------- #
    # helpers

    def create_fragment_with_version(self, scope, name, created_at_text):
        snippet = create_fragment(scope, name)
        self.db.session.add(snippet)

        created_at = datetime.strptime(created_at_text, '%Y-%m-%d %H:%M:%S')
        version = create_snippet_version(snippet, self.creator.id, created_at=created_at)
        self.db.session.add(version)

        current_version_association = create_current_version_association(snippet, version)
        self.db.session.add(current_version_association)

        self.db.session.commit()
        return version
