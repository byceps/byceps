"""Create a super user with admin privileges.

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

import click
from flask.cli import with_appcontext

from ...services.authorization import authz_service
from ...services.authorization.transfer.models import RoleID
from ...services.user import (
    user_command_service,
    user_creation_service,
    user_email_address_service,
)
from ...services.user.transfer.models import User
from ...typing import UserID


@click.command()
@click.option('--screen_name', prompt=True)
@click.option('--email_address', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
@with_appcontext
def create_superuser(screen_name, email_address, password) -> None:
    """Create a superuser with all roles assigned."""
    click.echo(f'Creating user "{screen_name}" ... ', nl=False)
    user = _create_user(screen_name, email_address, password)
    click.secho('done.', fg='green')

    click.echo(f'Initializing user "{screen_name}" ... ', nl=False)
    user_command_service.initialize_account(user.id)
    click.secho('done.', fg='green')

    user_email_address_service.confirm_email_address(user.id, email_address)

    role_ids = _get_role_ids()
    click.echo(
        f'Assigning {len(role_ids)} roles to user "{screen_name}" ... ',
        nl=False,
    )
    _assign_roles_to_user(role_ids, user.id)
    click.secho('done.', fg='green')


def _create_user(screen_name: str, email_address: str, password: str) -> User:
    try:
        user, event = user_creation_service.create_user(
            screen_name, email_address, password
        )
        return user
    except ValueError as e:
        raise click.UsageError(f'User creation failed: {e}')


def _get_role_ids() -> set[RoleID]:
    return authz_service.get_all_role_ids()


def _assign_roles_to_user(role_ids: set[RoleID], user_id: UserID) -> None:
    for role_id in role_ids:
        authz_service.assign_role_to_user(role_id, user_id)
