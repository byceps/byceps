"""
byceps.cli.cli
~~~~~~~~~~~~~~

Command-line interface

:Copyright: 2006-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click
from flask.cli import AppGroup

from .commands.create_database_tables import create_database_tables
from .commands.create_superuser import create_superuser
from .commands.export_roles import export_roles
from .commands.import_roles import import_roles


@click.group(cls=AppGroup)
def cli():
    pass


for func in [
    create_database_tables,
    create_superuser,
    export_roles,
    import_roles,
]:
    cli.add_command(func)
