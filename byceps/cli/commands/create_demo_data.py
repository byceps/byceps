"""
byceps.cli.command.create_demo_data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Populate the database with data for demonstration purposes.

:Copyright: 2014-2024 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""


import click
from flask.cli import with_appcontext

from byceps.services.authz import authz_service
from byceps.services.demo_data import demo_data_service
from byceps.services.user import user_command_service, user_creation_service
from byceps.services.user.models.user import User


@click.command()
@with_appcontext
def create_demo_data() -> None:
    """Generate data for demonstration purposes."""
    if demo_data_service.does_demo_data_exist():
        click.secho('Demonstration data already exists.', fg='yellow')
        return

    admin = _create_admin()

    demo_data_service.create_demo_data(admin)


def _create_admin() -> User:
    user, _ = user_creation_service.create_user(
        'DemoAdmin', 'admin@demo.example', 'demodemo', locale='en'
    ).unwrap()
    user_command_service.initialize_account(user)

    for role_id in authz_service.get_all_role_ids():
        authz_service.assign_role_to_user(role_id, user)

    return user
