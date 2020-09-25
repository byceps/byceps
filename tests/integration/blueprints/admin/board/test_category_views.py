"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.board import (
    category_command_service,
    category_query_service,
)

from tests.helpers import http_client


def test_create_form(admin_app, board_admin, board):
    url = f'/admin/boards/categories/for_board/{board.id}/create'
    response = get_resource(admin_app, board_admin, url)
    assert response.status_code == 200


def test_create(admin_app, board_admin, board):
    slug = 'off-topic'
    title = 'Off-Topic'
    description = 'Random stuff'

    assert category_query_service.find_category_by_slug(board.id, slug) is None

    url = f'/admin/boards/categories/for_board/{board.id}'
    form_data = {
        'slug': slug,
        'title': title,
        'description': description,
    }
    response = post_resource(admin_app, board_admin, url, form_data)

    category = category_query_service.find_category_by_slug(board.id, slug)
    assert category is not None
    assert category.id is not None
    assert category.slug == slug
    assert category.title == title
    assert category.description == description

    # Clean up.
    category_command_service.delete_category(category.id)


def test_update_form(admin_app, board_admin, category):
    url = f'/admin/boards/categories/{category.id}/update'
    response = get_resource(admin_app, board_admin, url)
    assert response.status_code == 200


# helpers


def get_resource(app, user, url):
    with http_client(app, user_id=user.id) as client:
        return client.get(url)


def post_resource(app, user, url, data):
    with http_client(app, user_id=user.id) as client:
        return client.post(url, data=data)
