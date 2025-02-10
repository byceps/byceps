"""
byceps.cli.cli
~~~~~~~~~~~~~~

Command-line interface

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click
from dotenv import load_dotenv
from flask.cli import AppGroup

from .commands.create_database_tables import create_database_tables
from .commands.create_superuser import create_superuser
from .commands.export_roles import export_roles
from .commands.generate_secret_key import generate_secret_key
from .commands.import_roles import import_roles
from .commands.import_seats import import_seats
from .commands.import_users import import_users
from .commands.initialize_database import initialize_database
from .commands.shell import shell
from .commands.worker import worker


load_dotenv()


@click.group(cls=AppGroup)
def cli():
    pass


for func in [
    create_database_tables,
    create_superuser,
    export_roles,
    generate_secret_key,
    import_roles,
    import_seats,
    import_users,
    initialize_database,
    shell,
    worker,
]:
    cli.add_command(func)
