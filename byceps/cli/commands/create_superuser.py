"""
byceps.cli.command.create_superuser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a superuser with admin privileges.

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

import click
from flask.cli import with_appcontext
from secret_type import secret

from byceps.services.authz import authz_service
from byceps.services.authz.models import RoleID
from byceps.services.user import (
    user_command_service,
    user_creation_service,
    user_email_address_service,
)
from byceps.services.user.models.user import Password, User


@click.command()
@click.option('--screen_name', prompt=True)
@click.option('--email_address', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
@with_appcontext
def create_superuser(screen_name, email_address, password) -> None:
    """Create a superuser with all roles assigned."""
    click.echo(f'Creating user "{screen_name}" ... ', nl=False)
    user = _create_user(screen_name, email_address, secret(password))
    click.secho('done.', fg='green')

    click.echo(f'Initializing user "{screen_name}" ... ', nl=False)
    user_command_service.initialize_account(user)
    click.secho('done.', fg='green')

    user_email_address_service.confirm_email_address(
        user, email_address
    ).unwrap()

    role_ids = _get_role_ids()
    click.echo(
        f'Assigning {len(role_ids)} roles to user "{screen_name}" ... ',
        nl=False,
    )
    _assign_roles_to_user(role_ids, user)
    click.secho('done.', fg='green')


def _create_user(
    screen_name: str, email_address: str, password: Password
) -> User:
    creation_result = user_creation_service.create_user(
        screen_name,
        email_address,
        password,
        creation_method='superuser creation command',
    )
    if creation_result.is_err():
        error_message = creation_result.unwrap_err()
        raise click.UsageError(f'User creation failed: {error_message}')

    user, event = creation_result.unwrap()

    return user


def _get_role_ids() -> set[RoleID]:
    return authz_service.get_all_role_ids()


def _assign_roles_to_user(role_ids: set[RoleID], user: User) -> None:
    for role_id in role_ids:
        authz_service.assign_role_to_user(role_id, user)
