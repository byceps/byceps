#!/usr/bin/env python

"""Import users from JSON lines.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.user import import_service

from _util import call_with_app_context


@click.command()
@click.argument('data_file', type=click.File())
def execute(data_file) -> None:
    lines = import_service.parse_lines(data_file)
    for line_number, line in enumerate(lines, start=1):
        try:
            user_dict = import_service.parse_user_json(line)
            user = import_service.create_user(user_dict)
            click.secho(
                f'[line {line_number}] Imported user {user.screen_name}.',
                fg='green',
            )
        except Exception as e:
            click.secho(
                f'[line {line_number}] Could not import user: {e}', fg='red'
            )


if __name__ == '__main__':
    call_with_app_context(execute)
