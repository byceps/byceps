"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.snippet import (
    mountpoint_service,
    service as snippet_service,
)


def test_index_mountpoints(snippet_admin_client, site):
    url = f'/admin/snippets/mountpoints/{site.id}'
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_create_mountpoint_form(
    snippet_admin_client, global_scope, snippet_admin
):
    _, event = snippet_service.create_fragment(
        global_scope, 'fragment1', snippet_admin.id, 'Body v1'
    )
    snippet_id = event.snippet_id

    url = f'/admin/snippets/snippets/{snippet_id}/mountpoints/create'
    response = snippet_admin_client.get(url)
    assert response.status_code == 200

    # Clean up.
    snippet_service.delete_snippet(snippet_id)


def test_create_mountpoint(
    snippet_admin_client, site, global_scope, snippet_admin
):
    _, event = snippet_service.create_fragment(
        global_scope, 'snippet1', snippet_admin.id, 'Body'
    )
    snippet_id = event.snippet_id

    url = f'/admin/snippets/snippets/{snippet_id}/mountpoints'
    form_data = {
        'site_id': site.id,
        'endpoint_suffix': 'test_suffix',
        'url_path': '/test',
    }
    response = snippet_admin_client.post(url, data=form_data)
    assert response.status_code == 302

    mountpoints = mountpoint_service.get_mountpoints_for_site(site.id)
    assert len(mountpoints) == 1

    mountpoint = list(mountpoints)[0]
    assert mountpoint.site_id == site.id
    assert mountpoint.endpoint_suffix == 'test_suffix'
    assert mountpoint.url_path == '/test'
    assert mountpoint.snippet_id == snippet_id

    # Clean up.
    mountpoint_service.delete_mountpoint(mountpoint.id)
    snippet_service.delete_snippet(snippet_id)


def test_delete_mountpoint(
    snippet_admin_client, site, global_scope, snippet_admin
):
    _, event = snippet_service.create_fragment(
        global_scope, 'snippet2', snippet_admin.id, 'Body'
    )
    snippet_id = event.snippet_id

    mountpoint = mountpoint_service.create_mountpoint(
        site.id, 'test', '/test', snippet_id
    )
    assert mountpoint_service.find_mountpoint(mountpoint.id) is not None

    url = f'/admin/snippets/mountpoints/{mountpoint.id}'
    response = snippet_admin_client.delete(url)
    assert response.status_code == 204

    assert mountpoint_service.find_mountpoint(mountpoint.id) is None
