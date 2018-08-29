#!/usr/bin/env python

"""Create a board for that brand.

:Copyright: 2006-2018 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.services.board import board_service
from byceps.util.system import get_config_filename_from_env_or_exit

from bootstrap.util import app_context
from bootstrap.validators import validate_brand


@click.command()
@click.argument('brand', callback=validate_brand)
@click.argument('board_id')
def execute(brand, board_id):
    board = board_service.create_board(brand.id, board_id)

    click.secho('Done.', fg='green')


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
