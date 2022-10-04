"""
:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.snippet import snippet_service


def test_index_for_scope(snippet_admin_client, global_scope):
    scope = global_scope

    url = f'/admin/snippets/for_scope/{scope.type_}/{scope.name}'
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_view_current_version(snippet_admin_client, make_snippet):
    _, event = make_snippet()
    snippet_id = event.snippet_id

    url = f'/admin/snippets/snippets/{snippet_id}/current_version'
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_view_version(snippet_admin_client, make_snippet):
    version, event = make_snippet()

    url = f'/admin/snippets/versions/{version.id}'
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_history(snippet_admin_client, make_snippet):
    _, event = make_snippet()
    snippet_id = event.snippet_id

    url = f'/admin/snippets/snippets/{snippet_id}/history'
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_compare_versions(snippet_admin_client, snippet_admin, make_snippet):
    version1, event = make_snippet()
    snippet_id = event.snippet_id

    version2, _ = snippet_service.update_snippet(
        snippet_id, snippet_admin.id, 'Body v2'
    )

    url = f'/admin/snippets/versions/{version1.id}/compare_to/{version2.id}'
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_create_form(snippet_admin_client, global_scope):
    scope = global_scope

    url = f'/admin/snippets/for_scope/{scope.type_}/{scope.name}/create'
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_delete(snippet_admin_client, make_snippet):
    _, event = make_snippet()
    snippet_id = event.snippet_id

    url = f'/admin/snippets/snippets/{snippet_id}'
    response = snippet_admin_client.delete(url)
    assert response.status_code == 204

    assert snippet_service.find_snippet(snippet_id) is None
