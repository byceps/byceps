"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import pytest

from byceps.services.snippet import snippet_service
from byceps.services.snippet.models import SnippetScope


CONTENT_TYPE_JSON = 'application/json'


def test_get_snippet_by_name(
    scope: SnippetScope, admin_user, api_client, api_client_authz_header
):
    language_code = 'en'
    snippet_version, _ = snippet_service.create_snippet(
        scope, 'infos', language_code, admin_user, 'TBD'
    )
    snippet_name = snippet_version.snippet.name

    response = send_request(
        api_client, api_client_authz_header, scope, snippet_name, language_code
    )

    assert response.status_code == 200
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON

    response_data = response.json
    assert response_data['content'] == {
        'body': 'TBD',
    }
    assert response_data['version'] == str(snippet_version.id)


def test_get_unknown_snippet_by_name(
    scope: SnippetScope, api_client, api_client_authz_header
):
    snippet_name = 'unknown-af'
    language_code = 'en'

    response = send_request(
        api_client, api_client_authz_header, scope, snippet_name, language_code
    )

    assert response.status_code == 404
    assert response.content_type == CONTENT_TYPE_JSON
    assert response.mimetype == CONTENT_TYPE_JSON
    assert response.json == {}


@pytest.fixture(scope='module')
def scope(site) -> SnippetScope:
    return SnippetScope.for_site(site.id)


# helpers


def send_request(
    api_client,
    api_client_authz_header,
    scope: SnippetScope,
    snippet_name,
    language_code,
):
    url = f'/api/v1/snippets/by_name/{scope.type_}/{scope.name}/{snippet_name}/{language_code}'
    headers = [api_client_authz_header]

    return api_client.get(url, headers=headers)
