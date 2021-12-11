"""
byceps.services.authorization.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2021 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from __future__ import annotations
from collections import defaultdict
from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from ...database import db
from ...typing import UserID

from ..user import log_service as user_log_service, service as user_service
from ..user.transfer.models import User

from .dbmodels import (
    Role as DbRole,
    RolePermission as DbRolePermission,
    UserRole as DbUserRole,
)
from .transfer.models import PermissionID, Role, RoleID


def create_role(
    role_id: RoleID, title: str, *, ignore_if_exists: bool = False
) -> Role:
    """Create a role."""
    role = DbRole(role_id, title)

    db.session.add(role)

    if ignore_if_exists:
        _commit_ignoring_integrity_error()
    else:
        db.session.commit()

    return _db_entity_to_role(role)


def delete_role(role_id: RoleID) -> None:
    """Delete a role."""
    db.session.query(DbRolePermission) \
        .filter_by(role_id=role_id) \
        .delete()

    db.session.query(DbRole) \
        .filter_by(id=role_id) \
        .delete()

    db.session.commit()


def find_role(role_id: RoleID) -> Optional[Role]:
    """Return the role with that id, or `None` if not found."""
    role = db.session.query(DbRole).get(role_id)

    if role is None:
        return None

    return _db_entity_to_role(role)


def find_role_ids_for_user(user_id: UserID) -> set[RoleID]:
    """Return the IDs of the roles assigned to the user."""
    roles = db.session \
        .query(DbRole) \
        .join(DbUserRole) \
        .filter(DbUserRole.user_id == user_id) \
        .all()

    return {r.id for r in roles}


def find_user_ids_for_role(role_id: RoleID) -> set[UserID]:
    """Return the IDs of the users that have this role assigned."""
    rows = db.session \
        .query(DbUserRole.user_id) \
        .filter(DbUserRole.role_id == role_id) \
        .all()

    return {row[0] for row in rows}


def assign_permission_to_role(
    permission_id: PermissionID, role_id: RoleID
) -> None:
    """Assign the permission to the role."""
    role_permission = DbRolePermission(role_id, permission_id)

    db.session.add(role_permission)
    db.session.commit()


def deassign_permission_from_role(
    permission_id: PermissionID, role_id: RoleID
) -> None:
    """Dessign the permission from the role."""
    role_permission = db.session.query(DbRolePermission) \
        .get((role_id, permission_id))

    if role_permission is None:
        raise ValueError('Unknown role ID and/or permission ID.')

    db.session.delete(role_permission)
    db.session.commit()


def assign_role_to_user(
    role_id: RoleID, user_id: UserID, *, initiator_id: Optional[UserID] = None
) -> None:
    """Assign the role to the user."""
    if _is_role_assigned_to_user(role_id, user_id):
        # Role is already assigned to user. Nothing to do.
        return

    user_role = DbUserRole(user_id, role_id)
    db.session.add(user_role)

    log_entry_data = {'role_id': str(role_id)}
    if initiator_id is not None:
        log_entry_data['initiator_id'] = str(initiator_id)
    log_entry = user_log_service.build_log_entry(
        'role-assigned', user_id, log_entry_data
    )
    db.session.add(log_entry)

    db.session.commit()


def deassign_role_from_user(
    role_id: RoleID, user_id: UserID, initiator_id: Optional[UserID] = None
) -> None:
    """Deassign the role from the user."""
    user_role = db.session.query(DbUserRole).get((user_id, role_id))

    if user_role is None:
        raise ValueError(
            f'Unknown role ID "{role_id}" and/or user ID "{user_id}".'
        )

    db.session.delete(user_role)

    log_entry_data = {'role_id': str(role_id)}
    if initiator_id is not None:
        log_entry_data['initiator_id'] = str(initiator_id)
    log_entry = user_log_service.build_log_entry(
        'role-deassigned', user_id, log_entry_data
    )
    db.session.add(log_entry)

    db.session.commit()


def deassign_all_roles_from_user(
    user_id: UserID, initiator_id: Optional[UserID] = None, commit: bool = True
) -> None:
    """Deassign all roles from the user."""
    table = DbUserRole.__table__
    delete_query = table.delete() \
        .where(table.c.user_id == user_id)
    db.session.execute(delete_query)

    if commit:
        db.session.commit()


def _is_role_assigned_to_user(role_id: RoleID, user_id: UserID) -> bool:
    """Determine if the role is assigned to the user or not."""
    subquery = db.session \
        .query(DbUserRole) \
        .filter_by(role_id=role_id) \
        .filter_by(user_id=user_id) \
        .exists()

    return db.session.query(subquery).scalar()


def get_permission_ids_for_user(user_id: UserID) -> set[PermissionID]:
    """Return the IDs of all permissions the user has through the roles
    assigned to it.
    """
    role_permissions = db.session \
        .query(DbRolePermission) \
        .join(DbRole) \
        .join(DbUserRole) \
        .filter(DbUserRole.user_id == user_id) \
        .all()

    return {rp.permission_id for rp in role_permissions}


def get_assigned_roles_for_permissions() -> dict[PermissionID, set[RoleID]]:
    """Return the IDs of roles that have permissions assigned, indexed
    by permission ID.
    """
    role_ids_by_permission_id = defaultdict(set)

    rows = db.session.execute(
        select(DbRolePermission.permission_id, DbRolePermission.role_id)
    ).all()

    permission_ids_and_role_ids = [
        (PermissionID(permission_id), RoleID(role_id))
        for permission_id, role_id in rows
    ]

    for permission_id, role_id in permission_ids_and_role_ids:
        role_ids_by_permission_id[permission_id].add(role_id)

    return dict(role_ids_by_permission_id)


def get_all_role_ids() -> set[RoleID]:
    """Return all role IDs."""
    return db.session.execute(
        select(DbRole.id)
    ).scalars().all()


def get_all_roles_with_permissions_and_users() -> list[
    tuple[Role, set[PermissionID], set[User]]
]:
    """Return all roles with titles, permission IDs, and assigned users."""
    db_roles = db.session.execute(
        select(DbRole)
        .options(
            db.undefer(DbRole.title),
            db.joinedload(DbRole.user_roles)
                .joinedload(DbUserRole.user)
        )
    ).scalars().unique().all()

    return [
        (
            _db_entity_to_role(db_role),
            {
                role_permission.permission_id
                for role_permission in db_role.role_permissions
            },
            {
                user_service._db_entity_to_user(db_user)
                for db_user in db_role.users
            },
        )
        for db_role in db_roles
    ]


def get_permission_ids_by_role() -> dict[Role, frozenset[PermissionID]]:
    """Return all roles with their assigned permission IDs.

    Role titles are undeferred to avoid lots of additional queries.
    """
    db_roles = db.session.execute(
        select(DbRole)
        .options(db.undefer(DbRole.title))
    ).scalars().unique().all()

    role_ids_and_permission_ids = db.session.execute(
        select(DbRolePermission.role_id, DbRolePermission.permission_id)
    ).all()

    return _index_permission_ids_by_role(role_ids_and_permission_ids, db_roles)


def get_permission_ids_by_role_for_user(
    user_id: UserID,
) -> dict[Role, frozenset[PermissionID]]:
    """Return permission IDs grouped by their respective roles for that
    user.

    Role titles are undeferred to avoid lots of additional queries.
    """
    db_roles = db.session.execute(
        select(DbRole)
        .options(db.undefer(DbRole.title))
        .join(DbUserRole)
        .filter(DbUserRole.user_id == user_id)
    ).scalars().unique().all()

    role_ids_and_permission_ids = db.session.execute(
        select(DbRolePermission.role_id, DbRolePermission.permission_id)
        .join(DbRole)
        .join(DbUserRole)
        .filter(DbUserRole.user_id == user_id)
    ).all()

    return _index_permission_ids_by_role(role_ids_and_permission_ids, db_roles)


def _index_permission_ids_by_role(
    role_ids_and_permission_ids: Iterable[tuple[RoleID, PermissionID]],
    db_roles: Iterable[DbRole],
) -> dict[Role, frozenset[PermissionID]]:
    """Index permission IDs by role."""
    permission_ids_by_role_id = defaultdict(set)
    for role_id, permission_id in role_ids_and_permission_ids:
        permission_ids_by_role_id[role_id].add(permission_id)

    permission_ids_by_role = {}

    for db_role in db_roles:
        role = _db_entity_to_role(db_role)
        permission_ids = frozenset(permission_ids_by_role_id[role.id])
        permission_ids_by_role[role] = permission_ids

    return permission_ids_by_role


def get_permission_ids_for_role(role_id: RoleID) -> set[PermissionID]:
    """Return the permission IDs assigned to the role."""
    permission_ids = db.session.execute(
        select(DbRolePermission.permission_id)
        .filter_by(role_id=role_id)
    ).scalars().all()

    return {PermissionID(permission_id) for permission_id in permission_ids}


def _commit_ignoring_integrity_error() -> None:
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


def _db_entity_to_role(role: DbRole) -> Role:
    return Role(
        role.id,
        role.title,
    )
