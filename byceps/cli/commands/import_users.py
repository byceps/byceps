"""Import user accounts from JSON lines.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click
from flask.cli import with_appcontext

from ...services.user import user_import_service


@click.command()
@click.argument('data_file', type=click.File())
@with_appcontext
def import_users(data_file) -> None:
    """Import user accounts."""
    lines = user_import_service.parse_lines(data_file)
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
