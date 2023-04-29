"""
byceps.cli.command.initialize_database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Initialize the database.

- Create tables.
- Import authorization roles.
- Add supported languages.

Existing tables will be ignored.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click
from flask.cli import with_appcontext

from byceps.services.language import language_service

from .create_database_tables import _create_database_tables
from .import_roles import _DEFAULT_DATA_FILE, _import_roles


@click.command()
@with_appcontext
def initialize_database() -> None:
    """Initialize the database."""
    _create_database_tables()
    _import_roles(_DEFAULT_DATA_FILE)
    _add_languages()


def _add_languages() -> None:
    for code in ('en', 'de'):
        click.echo(f'Adding language "{code}" ... ', nl=False)
        language_service.create_language(code)
        click.secho('done. ', fg='green')
