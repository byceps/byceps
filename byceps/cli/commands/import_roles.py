"""Import roles and their assigned permissions from a TOML file.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click
from flask.cli import with_appcontext

from ...services.authorization import impex_service


@click.command()
@click.argument('data_file', type=click.File())
@with_appcontext
def import_roles(data_file) -> None:
    """Import authorization roles."""
    role_count = impex_service.import_from_file(data_file)
    click.secho(f'Imported {role_count} roles.', fg='green')
