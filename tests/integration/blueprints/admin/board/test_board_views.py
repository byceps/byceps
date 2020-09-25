"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.services.board import board_service

from tests.helpers import http_client


def test_index_for_brand(admin_app, board_admin, brand, board):
    url = f'/admin/boards/brands/{brand.id}'
    response = get_resource(admin_app, board_admin, url)
    assert response.status_code == 200


def test_view(admin_app, board_admin, board):
    url = f'/admin/boards/boards/{board.id}'
    response = get_resource(admin_app, board_admin, url)
    assert response.status_code == 200


def test_create_form(admin_app, board_admin, brand):
    url = f'/admin/boards/for_brand/{brand.id}/boards/create'
    response = get_resource(admin_app, board_admin, url)
    assert response.status_code == 200


def test_create(admin_app, board_admin, brand):
    board_id = 'intranet-board-2018'

    assert board_service.find_board(board_id) is None

    url = f'/admin/boards/for_brand/{brand.id}/boards'
    form_data = {
        'board_id': board_id,
    }
    response = post_resource(admin_app, board_admin, url, form_data)

    board = board_service.find_board(board_id)
    assert board is not None
    assert board.id == board_id
    assert board.brand_id == brand.id

    # Clean up.
    board_service.delete_board(board_id)


# helpers


def get_resource(app, user, url):
    with http_client(app, user_id=user.id) as client:
        return client.get(url)


def post_resource(app, user, url, data):
    with http_client(app, user_id=user.id) as client:
        return client.post(url, data=data)
