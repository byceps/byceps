"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.snippet import service as snippet_service


def test_index_for_scope(snippet_admin_client, global_scope):
    scope = global_scope

    url = f'/admin/snippets/for_scope/{scope.type_}/{scope.name}'
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_view_current_version(snippet_admin_client, make_document):
    _, event = make_document()
    snippet_id = event.snippet_id

    url = f'/admin/snippets/snippets/{snippet_id}/current_version'
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_view_version(snippet_admin_client, make_document):
    version, event = make_document()

    url = f'/admin/snippets/versions/{version.id}'
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_history(snippet_admin_client, make_document):
    _, event = make_document()
    snippet_id = event.snippet_id

    url = f'/admin/snippets/snippets/{snippet_id}/history'
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_compare_documents(snippet_admin_client, snippet_admin, make_document):
    version1, event = make_document()
    snippet_id = event.snippet_id

    version2, _ = snippet_service.update_document(
        snippet_id, snippet_admin.id, 'Title v2', 'Body v2'
    )

    url = f'/admin/snippets/documents/{version1.id}/compare_to/{version2.id}'
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_compare_fragments(snippet_admin_client, snippet_admin, make_fragment):
    version1, event = make_fragment()
    snippet_id = event.snippet_id

    version2, _ = snippet_service.update_fragment(
        snippet_id, snippet_admin.id, 'Body v2'
    )

    url = f'/admin/snippets/fragments/{version1.id}/compare_to/{version2.id}'
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_create_document_form(
    snippet_admin_client, global_scope, make_fragment
):
    scope = global_scope

    url = (
        f'/admin/snippets/for_scope/{scope.type_}/{scope.name}/documents/create'
    )
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_create_fragment_form(snippet_admin_client, global_scope):
    scope = global_scope

    url = (
        f'/admin/snippets/for_scope/{scope.type_}/{scope.name}/fragments/create'
    )
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_delete_snippet(snippet_admin_client, make_fragment):
    _, event = make_fragment()
    snippet_id = event.snippet_id

    url = f'/admin/snippets/snippets/{snippet_id}'
    response = snippet_admin_client.delete(url)
    assert response.status_code == 204

    assert snippet_service.find_snippet(snippet_id) is None
