#!/usr/bin/env python

"""Import roles and their assigned permissions from a TOML file.

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click
from flask.cli import with_appcontext

from byceps.services.authorization import impex_service


@click.command()
@click.argument('data_file', type=click.File())
@with_appcontext
def execute(data_file) -> None:
    role_count = impex_service.import_from_file(data_file)
    click.secho(f'Imported {role_count} roles.', fg='green')


if __name__ == '__main__':
    execute()
