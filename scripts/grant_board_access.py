#!/usr/bin/env python

"""Grant access to a board to a user.

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.services.board import access_control_service, board_service
from byceps.services.board.transfer.models import Board
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context
from _validators import validate_user_screen_name



def validate_board(ctx, param, board_id: str) -> Board:
    board = board_service.find_board(board_id)

    if not board:
        raise click.BadParameter(f'Unknown board ID "{board_id}".')

    return board


@click.command()
@click.argument('board', metavar='BOARD_ID', callback=validate_board)
@click.argument(
    'user', metavar='USER_SCREEN_NAME', callback=validate_user_screen_name
)
def execute(board, user):
    if access_control_service.has_user_access_to_board(user.id, board.id):
        click.secho(f'User "{user.screen_name}" already has access '
                    f'to board "{board.id}".',
                    fg='yellow')
        return

    access_control_service.grant_access_to_board(board.id, user.id)

    click.secho(f'Access to board "{board.id}" granted '
                f'to user "{user.screen_name}".',
                fg='green')


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
