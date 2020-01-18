#!/usr/bin/env python

"""Import permissions, roles, and their relations from a JSON file.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import json

import click

from byceps.services.authorization import service as authz_service
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context


@click.command()
@click.argument('json_file', type=click.File())
def execute(json_file):
    data = json.load(json_file)

    permissions = data['permissions']
    roles = data['roles']

    click.echo(f'Importing {len(permissions)} permissions ... ', nl=False)
    create_permissions(permissions)
    click.secho('done.', fg='green')

    click.echo(f'Importing {len(roles)} roles ... ', nl=False)
    create_roles(roles)
    click.secho('done.', fg='green')


def create_permissions(permissions):
    for permission in permissions:
        authz_service.create_permission(permission['id'], permission['title'])


def create_roles(roles):
    for role in roles:
        role_id = role['id']

        authz_service.create_role(role_id, role['title'])

        for permission_id in role['assigned_permissions']:
            authz_service.assign_permission_to_role(permission_id, role_id)


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
