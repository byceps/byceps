#!/usr/bin/env python

"""Create an initial user with admin privileges to begin BYCEPS setup.

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Iterable, Sequence

import click

from byceps.services.authorization.dbmodels import Role as DbRole
from byceps.services.authorization import service as authorization_service
from byceps.services.user import command_service as user_command_service
from byceps.services.user import creation_service as user_creation_service
from byceps.services.user.transfer.models import User
from byceps.typing import UserID

from _util import call_with_app_context


@click.command()
@click.option('--screen_name', prompt=True)
@click.option('--email_address', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
def execute(screen_name, email_address, password) -> None:
    click.echo(f'Creating user "{screen_name}" ... ', nl=False)
    user = _create_user(screen_name, email_address, password)
    click.secho('done.', fg='green')

    click.echo(f'Initializing user "{screen_name}" ... ', nl=False)
    user_command_service.initialize_account(user.id)
    click.secho('done.', fg='green')

    roles = _get_roles()
    click.echo(
        f'Assigning {len(roles)} roles to user "{screen_name}" ... ', nl=False
    )
    _assign_roles_to_user(roles, user.id)
    click.secho('done.', fg='green')


def _create_user(screen_name: str, email_address: str, password: str) -> User:
    try:
        user, event = user_creation_service.create_basic_user(
            screen_name, email_address, password
        )
        return user
    except ValueError as e:
        raise click.UsageError('User creation failed: {e}')


def _get_roles() -> Sequence[DbRole]:
    return authorization_service.get_all_roles_with_titles()


def _assign_roles_to_user(roles: Iterable[DbRole], user_id: UserID) -> None:
    for role in roles:
        authorization_service.assign_role_to_user(role.id, user_id)


if __name__ == '__main__':
    call_with_app_context(execute)
