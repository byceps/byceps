#!/usr/bin/env python

"""Export all permissions, roles, and their relations as TOML to STDOUT.

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

import sys

import click
import rtoml

from byceps.database import db
from byceps.services.authorization.models import Permission, Role
from byceps.util.system import get_config_filename_from_env_or_exit

from _util import app_context


@click.command()
def execute():
    permissions = list(collect_permissions())
    roles = list(collect_roles())

    data = {
        'permissions': permissions,
        'roles': roles,
    }

    rtoml.dump(data, sys.stdout, pretty=True)


def collect_permissions():
    """Collect all permissions, even those not assigned to any role."""
    permissions = Permission.query \
        .options(
            db.undefer('title'),
        ) \
        .order_by(Permission.id) \
        .all()

    for permission in permissions:
        yield {
            'id': permission.id,
            'title': permission.title,
        }


def collect_roles():
    """Collect all roles and the permissions assigned to them."""
    roles = Role.query \
        .options(
            db.undefer('title'),
            db.joinedload('role_permissions'),
        ) \
        .order_by(Role.id) \
        .all()

    for role in roles:
        permission_ids = [permission.id for permission in role.permissions]
        permission_ids.sort()

        yield {
            'id': role.id,
            'title': role.title,
            'assigned_permissions': permission_ids,
        }


if __name__ == '__main__':
    config_filename = get_config_filename_from_env_or_exit()
    with app_context(config_filename):
        execute()
