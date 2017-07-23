#!/usr/bin/env python
"""Create an initial user with admin privileges to begin BYCEPS setup.

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.database import db
from byceps.services.authentication.password import service as password_service
from byceps.services.user import creation_service as user_creation_service
from byceps.util.system import get_config_filename_from_env_or_exit

from bootstrap.util import app_context


@click.command()
@click.option('--screen_name', prompt=True)
@click.option('--email_address', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
def execute(screen_name, email_address, password):
    click.echo('Creating user "{}" ... '.format(screen_name), nl=False)

    user = _create_user(screen_name, email_address)
    password_service.create_password_hash(user.id, password)

    click.secho('done.', fg='green')


def _create_user(screen_name, email_address):
    try:
        user = user_creation_service.build_user(screen_name, email_address)
    except ValueError as e:
        raise click.UsageError(e)

    user.enabled = True
    db.session.add(user)
    db.session.commit()

    return user


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
