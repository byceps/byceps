#!/usr/bin/env python

"""Create an initial user with admin privileges to begin BYCEPS setup.

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import click

from byceps.services.authorization import service as authorization_service
from byceps.services.user import command_service as user_command_service
from byceps.services.user import creation_service as user_creation_service
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context


@click.command()
@click.option('--screen_name', prompt=True)
@click.option('--email_address', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
def execute(screen_name, email_address, password):
    click.echo(f'Creating user "{screen_name}" ... ', nl=False)
    user = _create_user(screen_name, email_address, password)
    click.secho('done.', fg='green')

    click.echo(f'Enabling user "{screen_name}" ... ', nl=False)
    user_command_service.enable_user(user.id, user.id)
    click.secho('done.', fg='green')

    roles = _get_roles()
    click.echo(
        f'Assigning {len(roles)} roles to user "{screen_name}" ... ', nl=False
    )
    _assign_roles_to_user(roles, user.id)
    click.secho('done.', fg='green')


def _create_user(screen_name, email_address, password):
    try:
        return user_creation_service.create_basic_user(
            screen_name, email_address, password
        )
    except ValueError as e:
        raise click.UsageError(e)


def _get_roles():
    return authorization_service.get_all_roles_with_titles()


def _assign_roles_to_user(roles, user_id):
    for role in roles:
        authorization_service.assign_role_to_user(role.id, user_id)


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
