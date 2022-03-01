"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.snippet import service as snippet_service
from byceps.services.snippet.transfer.models import Scope


CONTENT_TYPE_JSON = 'application/json'


def test_get_snippet_document_by_name(
    scope, admin_user, api_client, api_client_authz_header
):
    snippet_version, _ = snippet_service.create_document(
        scope, 'colophon', admin_user.id, 'Colophon', 'Made with BYCEPS.'
    )
    snippet_name = snippet_version.snippet.name

    response = send_request(
        api_client, api_client_authz_header, scope, snippet_name
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


def test_get_snippet_fragment_by_name(
    scope, admin_user, api_client, api_client_authz_header
):
    snippet_version, _ = snippet_service.create_fragment(
        scope, 'infos', admin_user.id, 'TBD'
    )
    snippet_name = snippet_version.snippet.name

    response = send_request(
        api_client, api_client_authz_header, scope, snippet_name
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


def test_get_unknown_snippet_by_name(
    scope, api_client, api_client_authz_header
):
    snippet_name = 'unknown-af'

    response = send_request(
        api_client, api_client_authz_header, scope, snippet_name
    )

    assert response.status_code == 404
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON
    assert response.json == {}


@pytest.fixture(scope='module')
def scope(site):
    return Scope.for_site(site.id)


# helpers


def send_request(api_client, api_client_authz_header, scope, snippet_name):
    url = f'/api/v1/snippets/by_name/{scope.type_}/{scope.name}/{snippet_name}'
    headers = [api_client_authz_header]

    return api_client.get(url, headers=headers)
