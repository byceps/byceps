"""
:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from byceps.services.board import board_service


def test_index_for_brand(board_admin_client, brand, board):
    url = f'/admin/boards/brands/{brand.id}'
    response = board_admin_client.get(url)
    assert response.status_code == 200


def test_view(board_admin_client, board):
    url = f'/admin/boards/boards/{board.id}'
    response = board_admin_client.get(url)
    assert response.status_code == 200


def test_create_form(board_admin_client, brand):
    url = f'/admin/boards/for_brand/{brand.id}/boards/create'
    response = board_admin_client.get(url)
    assert response.status_code == 200


def test_create(board_admin_client, brand):
    board_id = 'intranet-board-2018'

    assert board_service.find_board(board_id) is None

    url = f'/admin/boards/for_brand/{brand.id}/boards'
    form_data = {
        'board_id': board_id,
    }
    response = board_admin_client.post(url, data=form_data)

    board = board_service.find_board(board_id)
    assert board is not None
    assert board.id == board_id
    assert board.brand_id == brand.id

    # Clean up.
    board_service.delete_board(board_id)
