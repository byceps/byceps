"""
byceps.cli.command.import_users
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Import user accounts from JSON lines.

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path

import click
from flask.cli import with_appcontext

from byceps.services.user import user_import_service


@click.command()
@click.argument(
    'data_file', type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@with_appcontext
def import_users(data_file: Path) -> None:
    """Import user accounts."""
    with data_file.open() as f:
        lines = user_import_service.parse_lines(f)
        for line_number, line in enumerate(lines, start=1):
            try:
                user_to_import = user_import_service.parse_user_json(line)
                user = user_import_service.import_user(user_to_import)
                click.secho(
                    f'[line {line_number}] Imported user {user.screen_name}.',
                    fg='green',
                )
            except Exception as e:
                click.secho(
                    f'[line {line_number}] Could not import user: {e}', fg='red'
                )
