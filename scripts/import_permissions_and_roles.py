#!/usr/bin/env python

"""Import permissions, roles, and their relations from a TOML file.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.services.authorization import impex_service

from _util import call_with_app_context


@click.command()
@click.argument('data_file', type=click.File())
def execute(data_file) -> None:
    permission_count, role_count = impex_service.import_from_file(data_file)
    click.secho(
        f'Imported {permission_count} permissions and {role_count} roles.',
        fg='green',
    )


if __name__ == '__main__':
    call_with_app_context(execute)
