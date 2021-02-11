"""
byceps.services.authorization.impex_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Import/export

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path
from typing import Dict, Iterator, List, Tuple, Union

import rtoml

from ...database import db

from .dbmodels import Permission as DbPermission, Role as DbRole
from . import service


# -------------------------------------------------------------------- #
# import


def import_from_file(path: Path) -> Tuple[int, int]:
    """Import permissions, roles, and their relations from TOML."""
    data = rtoml.load(path)

    permissions = data['permissions']
    roles = data['roles']

    _create_permissions(permissions)
    _create_roles(roles)

    return len(permissions), len(roles)


def _create_permissions(permissions: List[Dict[str, str]]) -> None:
    for permission in permissions:
        service.create_permission(permission['id'], permission['title'])


def _create_roles(roles: List[Dict[str, Union[str, List[str]]]]) -> None:
    for role in roles:
        role_id = role['id']

        service.create_role(role_id, role['title'])

        for permission_id in role['assigned_permissions']:
            service.assign_permission_to_role(permission_id, role_id)


# -------------------------------------------------------------------- #
# export


def export() -> str:
    """Export all permissions, roles, and their relations as TOML."""
    permissions = list(_collect_permissions())
    roles = list(_collect_roles())

    data = {
        'permissions': permissions,
        'roles': roles,
    }

    return rtoml.dumps(data, pretty=True)


def _collect_permissions() -> Iterator[Dict[str, str]]:
    """Collect all permissions, even those not assigned to any role."""
    permissions = DbPermission.query \
        .options(
            db.undefer('title'),
        ) \
        .order_by(DbPermission.id) \
        .all()

    for permission in permissions:
        yield {
            'id': permission.id,
            'title': permission.title,
        }


def _collect_roles() -> Iterator[Dict[str, Union[str, List[str]]]]:
    """Collect all roles and the permissions assigned to them."""
    roles = DbRole.query \
        .options(
            db.undefer('title'),
            db.joinedload('role_permissions'),
        ) \
        .order_by(DbRole.id) \
        .all()

    for role in roles:
        permission_ids = [permission.id for permission in role.permissions]
        permission_ids.sort()

        yield {
            'id': role.id,
            'title': role.title,
            'assigned_permissions': permission_ids,
        }
