"""
:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from datetime import datetime

from byceps.database import db
from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope

from testfixtures.snippet import (
    create_current_version_association,
    create_fragment,
    create_snippet_version,
)

from tests.helpers import create_brand, create_party, create_user


def test_current_party_is_considered(admin_app_with_db, admin_user):
    brand = create_brand('lafiesta', 'La Fiesta')

    party2014 = create_party(brand.id, 'lafiesta-2014', 'La Fiesta 2014')
    party2015 = create_party(brand.id, 'lafiesta-2015', 'La Fiesta 2015')

    scope_site2014 = Scope.for_site(party2014.id)
    scope_site2015 = Scope.for_site(party2015.id)

    creator = admin_user

    fragment_info2014_version = create_fragment_with_version(
        scope_site2014, 'info', creator.id, '2014-10-23 14:55:00'
    )
    fragment_info2015_version = create_fragment_with_version(
        scope_site2015, 'info', creator.id, '2014-10-23 18:21:00'
    )

    actual = snippet_service.find_current_version_of_snippet_with_name(
        scope_site2014, 'info'
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


def create_fragment_with_version(scope, name, creator_id, created_at_text):
    snippet = create_fragment(scope, name)
    db.session.add(snippet)

    created_at = datetime.strptime(created_at_text, '%Y-%m-%d %H:%M:%S')
    version = create_snippet_version(snippet, creator_id, created_at=created_at)
    db.session.add(version)

    current_version_association = create_current_version_association(
        snippet, version
    )
    db.session.add(current_version_association)

    db.session.commit()
    return version
