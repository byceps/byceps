#!/usr/bin/env python

"""Create the initial database structure.

Existing tables will be ignored, and those not existing will be created.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click

from byceps.database import db

from _util import call_with_app_context


@click.command()
def execute() -> None:
    click.echo('Creating database tables ... ', nl=False)

    db.create_all()

    click.secho('done.', fg='green')


if __name__ == '__main__':
    call_with_app_context(execute)
