"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope

from tests.helpers import create_brand, create_party, create_user


def test_current_party_is_considered(admin_app_with_db, admin_user):
    brand = create_brand('lafiesta', 'La Fiesta')

    party2014 = create_party(brand.id, 'lafiesta-2014', 'La Fiesta 2014')
    party2015 = create_party(brand.id, 'lafiesta-2015', 'La Fiesta 2015')

    scope_site2014 = Scope.for_site(party2014.id)
    scope_site2015 = Scope.for_site(party2015.id)

    name = 'info'
    creator = admin_user

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


def test_unknown_name(admin_app_with_db):
    brand = create_brand('lafiesta', 'La Fiesta')

    party = create_party(brand.id, 'lafiesta-2014', 'La Fiesta 2014')

    scope = Scope.for_site(party.id)

    actual = snippet_service.find_current_version_of_snippet_with_name(
        scope, 'totally-unknown-snippet-name'
    )

    assert actual is None


# helpers


def create_fragment(scope, name, creator_id):
    body = ''
    version, _ = snippet_service.create_fragment(scope, name, creator_id, body)
    return version
