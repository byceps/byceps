"""Import roles and their assigned permissions from a TOML file.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path

import click
from flask.cli import with_appcontext

from ...services.authorization import impex_service


@click.command()
@click.argument(
    'data_file', type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@with_appcontext
def import_roles(data_file: Path) -> None:
    """Import authorization roles."""
    click.echo('Importing roles ... ', nl=False)
    role_count = impex_service.import_from_file(data_file)
    click.secho(f'done. Imported {role_count} roles.', fg='green')
