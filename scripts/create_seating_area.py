#!/usr/bin/env python

"""Create a seating area.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.seating import area_service
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context
from _validators import validate_party


@click.command()
@click.argument('party', callback=validate_party)
@click.argument('slug')
@click.argument('title')
def execute(party, slug, title):
    area_service.create_area(party.id, slug, title)
    click.secho('Done.', fg='green')


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
