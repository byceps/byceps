#!/usr/bin/env python

"""Import permissions, roles, and their relations from a TOML file.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.authorization import impex_service
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context


@click.command()
@click.argument('data_file', type=click.File())
def execute(data_file):
    permission_count, role_count = impex_service.import_from_file(data_file)
    click.secho(
        'Imported {permission_count} permissions and {role_count} roles.',
        fg='green',
    )


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
