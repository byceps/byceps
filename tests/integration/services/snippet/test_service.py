"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope


@pytest.fixture(scope='module')
def party1(make_party, brand):
    return make_party(brand.id, 'lafiesta-2014', 'La Fiesta 2014')


@pytest.fixture(scope='module')
def party2(make_party, brand):
    return make_party(brand.id, 'lafiesta-2015', 'La Fiesta 2015')


def test_current_party_is_considered(party1, party2, make_user):
    scope_site2014 = Scope.for_site(party1.id)
    scope_site2015 = Scope.for_site(party2.id)

    name = 'info'
    creator = make_user()

    fragment_info2014_version = create_fragment(
        scope_site2014, name, creator.id
    )
    fragment_info2015_version = create_fragment(
        scope_site2015, name, creator.id
    )

    actual = snippet_service.find_current_version_of_snippet_with_name(
        scope_site2014, name
    )

    assert actual == fragment_info2014_version

    for version in fragment_info2014_version, fragment_info2015_version:
        snippet_service.delete_snippet(version.snippet_id)


def test_unknown_name(party1):
    scope = Scope.for_site(party1.id)

    actual = snippet_service.find_current_version_of_snippet_with_name(
        scope, 'totally-unknown-snippet-name'
    )

    assert actual is None


# helpers


def create_fragment(scope, name, creator_id):
    body = ''
    version, _ = snippet_service.create_fragment(scope, name, creator_id, body)
    return version
