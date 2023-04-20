"""
:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

import pytest

from byceps.events.page import PageCreated
from byceps.services.page import page_service
from byceps.services.page.models import PageVersion
from byceps.services.site.models import Site
from byceps.services.user.models.user import User

from tests.helpers import generate_token, log_in_user


@pytest.fixture(scope='package')
def page_admin(make_admin):
    permission_ids = {
        'admin.access',
        'page.create',
        'page.update',
        'page.delete',
        'page.view',
        'page.view_history',
    }
    admin = make_admin(permission_ids)
    log_in_user(admin.id)
    return admin


@pytest.fixture(scope='package')
def page_admin_client(make_client, admin_app, page_admin):
    return make_client(admin_app, user_id=page_admin.id)


@pytest.fixture
def make_page(site: Site, page_admin: User):
    def _wrapper(
        name: Optional[str] = None,
        language_code: str = 'en',
        url_path: Optional[str] = None,
        title: str = 'Title',
        body: str = 'Body',
    ) -> tuple[PageVersion, PageCreated]:
        if name is None:
            name = generate_token()

        if url_path is None:
            url_path = f'/page-{generate_token()}'

        version, event = page_service.create_page(
            site.id, name, language_code, url_path, page_admin.id, title, body
        )
        return version, event

    return _wrapper


def test_index_for_site(page_admin_client, site):
    url = f'/admin/pages/for_site/{site.id}'
    response = page_admin_client.get(url)
    assert response.status_code == 200


def test_view_current_version(page_admin_client, make_page):
    _, event = make_page()
    page_id = event.page_id

    url = f'/admin/pages/pages/{page_id}/current_version'
    response = page_admin_client.get(url)
    assert response.status_code == 200


def test_view_version(page_admin_client, make_page):
    version, event = make_page()

    url = f'/admin/pages/versions/{version.id}'
    response = page_admin_client.get(url)
    assert response.status_code == 200


def test_history(page_admin_client, make_page):
    _, event = make_page()
    page_id = event.page_id

    url = f'/admin/pages/pages/{page_id}/history'
    response = page_admin_client.get(url)
    assert response.status_code == 200


def test_compare(page_admin_client, page_admin, make_page):
    version1, event = make_page()
    page_id = event.page_id

    page = page_service.get_page(page_id)

    version2, _ = page_service.update_page(
        page.id,
        page.language_code,
        page.url_path,
        page_admin.id,
        'Title v2',
        'Head v2',
        'Body v2',
    )

    url = f'/admin/pages/versions/{version1.id}/compare_to/{version2.id}'
    response = page_admin_client.get(url)
    assert response.status_code == 200


def test_create_form(page_admin_client, site):
    url = f'/admin/pages/for_site/{site.id}/create'
    response = page_admin_client.get(url)
    assert response.status_code == 200


def test_delete(page_admin_client, make_page):
    _, event = make_page()
    page_id = event.page_id

    url = f'/admin/pages/pages/{page_id}'
    response = page_admin_client.delete(url)
    assert response.status_code == 204

    assert page_service.find_page(page_id) is None
