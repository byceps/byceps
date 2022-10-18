"""
byceps.services.authorization.impex_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Import/export

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from pathlib import Path
from typing import Iterator, Union

import rtoml
from sqlalchemy import select

from ...database import db

from .dbmodels import DbRole
from .transfer.models import PermissionID, RoleID
from . import service


# -------------------------------------------------------------------- #
# import


def import_from_file(path: Path) -> int:
    """Import roles and their assigned permissions from TOML."""
    data = rtoml.load(path)

    roles = data['roles']

    _create_roles(roles)

    return len(roles)


def _create_roles(roles: list[dict[str, Union[str, list[str]]]]) -> None:
    for role in roles:
        role_id = RoleID(str(role['id']))
        role_title = str(role['title'])

        service.create_role(role_id, role_title)

        for permission_id_str in role['assigned_permissions']:
            permission_id = PermissionID(permission_id_str)
            service.assign_permission_to_role(permission_id, role_id)


# -------------------------------------------------------------------- #
# export


def export() -> str:
    """Export roles and their assigned permissions as TOML."""
    roles = list(_collect_roles())

    data = {'roles': roles}

    return rtoml.dumps(data, pretty=True)


def _collect_roles() -> Iterator[dict[str, Union[str, list[str]]]]:
    """Collect all roles and the permissions assigned to them."""
    roles = db.session.scalars(
        select(DbRole)
        .options(
            db.undefer(DbRole.title),
            db.joinedload(DbRole.role_permissions),
        )
        .order_by(DbRole.id)
    ).all()

    for role in roles:
        permission_ids = [
            role_permission.permission_id
            for role_permission in role.role_permissions
        ]
        permission_ids.sort()

        yield {
            'id': role.id,
            'title': role.title,
            'assigned_permissions': permission_ids,
        }
