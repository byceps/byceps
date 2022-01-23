"""
:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.snippet import mountpoint_service

from tests.helpers import generate_token


def test_index(snippet_admin_client, site):
    url = f'/admin/snippets/mountpoints/for_site/{site.id}'
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_site_select_form(snippet_admin_client, make_fragment):
    _, event = make_fragment()
    snippet_id = event.snippet_id

    url = f'/admin/snippets/mountpoints/for_snippet/{snippet_id}/select_site'
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_create_form(snippet_admin_client, site, make_fragment):
    _, event = make_fragment()
    snippet_id = event.snippet_id

    url = f'/admin/snippets/mountpoints/for_snippet/{snippet_id}/for_site/{site.id}/create'
    response = snippet_admin_client.get(url)
    assert response.status_code == 200


def test_create(snippet_admin_client, site, make_fragment):
    _, event = make_fragment()
    snippet_id = event.snippet_id
    endpoint_suffix = f'test_{generate_token()}'
    url_path = f'/test-{generate_token()}'

    url = f'/admin/snippets/mountpoints/for_snippet/{snippet_id}/for_site/{site.id}'
    form_data = {
        'endpoint_suffix': endpoint_suffix,
        'url_path': url_path,
    }
    response = snippet_admin_client.post(url, data=form_data)
    assert response.status_code == 302

    mountpoints = mountpoint_service.get_mountpoints_for_site(site.id)
    assert len(mountpoints) == 1

    mountpoint = list(mountpoints)[0]
    assert mountpoint.site_id == site.id
    assert mountpoint.endpoint_suffix == endpoint_suffix
    assert mountpoint.url_path == url_path
    assert mountpoint.snippet_id == snippet_id

    # Clean up.
    mountpoint_service.delete_mountpoint(mountpoint.id)


def test_delete(snippet_admin_client, site, make_fragment):
    _, event = make_fragment()
    snippet_id = event.snippet_id
    endpoint_suffix = f'test_{generate_token()}'
    url_path = f'/test-{generate_token()}'

    mountpoint = mountpoint_service.create_mountpoint(
        site.id, endpoint_suffix, url_path, snippet_id
    )
    assert mountpoint_service.find_mountpoint(mountpoint.id) is not None

    url = f'/admin/snippets/mountpoints/mountpoints/{mountpoint.id}'
    response = snippet_admin_client.delete(url)
    assert response.status_code == 204

    assert mountpoint_service.find_mountpoint(mountpoint.id) is None
