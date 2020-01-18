"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import pytest

from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope


CONTENT_TYPE_JSON = 'application/json'


def test_get_snippet_document_by_name(scope, admin, api_client):
    snippet_version, _ = snippet_service.create_document(
        scope, 'colophon', admin.id, 'Colophon', 'Made with BYCEPS.'
    )
    snippet_name = snippet_version.snippet.name

    response = api_client.get(
        f'/api/snippets/by_name/{scope.type_}/{scope.name}/{snippet_name}'
    )

    assert response.status_code == 200
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON

    response_data = response.json
    assert response_data['content'] == {
        'title': 'Colophon',
        'head': None,
        'body': 'Made with BYCEPS.',
    }
    assert response_data['type'] == 'document'
    assert response_data['version'] == str(snippet_version.id)


def test_get_snippet_fragment_by_name(scope, admin, api_client):
    snippet_version, _ = snippet_service.create_fragment(
        scope, 'infos', admin.id, 'TBD'
    )
    snippet_name = snippet_version.snippet.name

    response = api_client.get(
        f'/api/snippets/by_name/{scope.type_}/{scope.name}/{snippet_name}'
    )

    assert response.status_code == 200
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON

    response_data = response.json
    assert response_data['content'] == {
        'body': 'TBD',
    }
    assert response_data['type'] == 'fragment'
    assert response_data['version'] == str(snippet_version.id)


def test_get_unknown_snippet_by_name(scope, api_client):
    snippet_name = 'unknown-af'

    response = api_client.get(
        f'/api/snippets/by_name/{scope.type_}/{scope.name}/{snippet_name}'
    )

    assert response.status_code == 404
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON
    assert response.json == {}


@pytest.fixture(scope='module')
def scope(site):
    return Scope.for_site(site.id)
