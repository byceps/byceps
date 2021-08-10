#!/usr/bin/env python

"""Grant access to a board to a user.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.board import access_control_service, board_service
from byceps.services.board.transfer.models import Board, BoardID

from _util import call_with_app_context
from _validators import validate_user_screen_name


def validate_board(ctx, param, board_id_value: str) -> Board:
    board = board_service.find_board(BoardID(board_id_value))

    if not board:
        raise click.BadParameter(f'Unknown board ID "{board_id_value}".')

    return board


@click.command()
@click.argument('board', metavar='BOARD_ID', callback=validate_board)
@click.argument(
    'user', metavar='USER_SCREEN_NAME', callback=validate_user_screen_name
)
def execute(board, user) -> None:
    if access_control_service.has_user_access_to_board(user.id, board.id):
        click.secho(
            f'User "{user.screen_name}" already has access '
            f'to board "{board.id}".',
            fg='yellow',
        )
        return

    access_control_service.grant_access_to_board(board.id, user.id)

    click.secho(
        f'Access to board "{board.id}" granted '
        f'to user "{user.screen_name}".',
        fg='green',
    )


if __name__ == '__main__':
    call_with_app_context(execute)
