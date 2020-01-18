#!/usr/bin/env python

"""Create the initial database structure.

Existing tables will be ignored, and those not existing will be created.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.database import db
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context


@click.command()
def execute():
    click.echo('Creating database tables ... ', nl=False)

    db.create_all()

    click.secho('done.', fg='green')


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
