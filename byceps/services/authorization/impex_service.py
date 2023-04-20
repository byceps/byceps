"""
byceps.services.authorization.impex_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Import/export

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import rtoml
from sqlalchemy import select

from byceps.database import db

from . import authz_service
from .dbmodels import DbRole
from .models import PermissionID, RoleID


# -------------------------------------------------------------------- #
# import


def import_roles(path: Path) -> ImportedRoleCounts:
    """Import roles and their assigned permissions from TOML."""
    data = rtoml.load(path)
    roles = data['roles']
    return _create_roles(roles)


def _create_roles(
    roles: list[dict[str, str | list[str]]]
) -> ImportedRoleCounts:
    imported_roles_count = 0
    skipped_roles_count = 0

    for role in roles:
        role_id = RoleID(str(role['id']))
        role_title = str(role['title'])

        role_result = authz_service.create_role(role_id, role_title)
        if role_result.is_ok():
            imported_roles_count += 1
        else:
            # Role exists; skip.
            skipped_roles_count += 1
            continue

        for permission_id_str in role['assigned_permissions']:
            permission_id = PermissionID(permission_id_str)
            authz_service.assign_permission_to_role(permission_id, role_id)

    return ImportedRoleCounts(
        imported=imported_roles_count,
        skipped=skipped_roles_count,
    )


@dataclass(frozen=True)
class ImportedRoleCounts:
    imported: int
    skipped: int


# -------------------------------------------------------------------- #
# export


def export_roles() -> str:
    """Export roles and their assigned permissions as TOML."""
    roles = list(_collect_roles())
    data = {'roles': roles}
    return rtoml.dumps(data, pretty=True)


def _collect_roles() -> Iterator[dict[str, str | list[str]]]:
    """Collect all roles and the permissions assigned to them."""
    roles = (
        db.session.scalars(
            select(DbRole).options(db.undefer(DbRole.title)).order_by(DbRole.id)
        )
        .unique()
        .all()
    )

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
