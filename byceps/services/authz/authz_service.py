"""
byceps.services.authz.authz_service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from collections import defaultdict
from collections.abc import Iterable

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from byceps.database import db
from byceps.services.user import user_log_service, user_service
from byceps.services.user.models.log import UserLogEntry
from byceps.services.user.models.user import User, UserID
from byceps.util.result import Err, Ok, Result

from . import authz_domain_service
from .dbmodels import DbRole, DbRolePermission, DbUserRole
from .events import RoleAssignedToUserEvent, RoleDeassignedFromUserEvent
from .models import PermissionID, Role, RoleID


def create_role(role_id: RoleID, title: str) -> Result[Role, IntegrityError]:
    """Create a role."""
    db_role = DbRole(role_id, title)

    db.session.add(db_role)

    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        return Err(e)

    return Ok(db_role).map(_db_entity_to_role)


def delete_role(role_id: RoleID) -> None:
    """Delete a role."""
    db.session.execute(
        delete(DbRolePermission).where(DbRolePermission.role_id == role_id)
    )
    db.session.execute(delete(DbRole).where(DbRole.id == role_id))
    db.session.commit()


def find_role(role_id: RoleID) -> Role | None:
    """Return the role with that id, or `None` if not found."""
    db_role = db.session.get(DbRole, role_id)

    if db_role is None:
        return None

    return _db_entity_to_role(db_role)


def find_role_ids_for_user(user_id: UserID) -> set[RoleID]:
    """Return the IDs of the roles assigned to the user."""
    db_roles = (
        db.session.scalars(
            select(DbRole)
            .join(DbUserRole)
            .filter(DbUserRole.user_id == user_id)
        )
        .unique()
        .all()
    )

    return {db_role.id for db_role in db_roles}


def find_user_ids_for_role(role_id: RoleID) -> set[UserID]:
    """Return the IDs of the users that have this role assigned."""
    user_id_rows = db.session.scalars(
        select(DbUserRole.user_id).filter(DbUserRole.role_id == role_id)
    ).all()

    return set(user_id_rows)


def assign_permission_to_role(
    permission_id: PermissionID, role_id: RoleID
) -> None:
    """Assign the permission to the role."""
    db_role_permission = DbRolePermission(role_id, permission_id)

    db.session.add(db_role_permission)
    db.session.commit()


def deassign_permission_from_role(
    permission_id: PermissionID, role_id: RoleID
) -> Result[None, str]:
    """Deassign the permission from the role."""
    db_role_permission = db.session.get(
        DbRolePermission, (role_id, permission_id)
    )

    if db_role_permission is None:
        return Err('Unknown role ID and/or permission ID')

    db.session.delete(db_role_permission)
    db.session.commit()

    return Ok(None)


def assign_role_to_user(
    role_id: RoleID, user: User, *, initiator: User | None = None
) -> RoleAssignedToUserEvent | None:
    """Assign the role to the user."""
    if _is_role_assigned_to_user(role_id, user.id):
        # Role is already assigned to user. Nothing to do.
        return None

    event, log_entry = authz_domain_service.assign_role_to_user(
        role_id, user, initiator=initiator
    )

    _persist_role_assignment_to_user(role_id, user, log_entry)

    return event


def _persist_role_assignment_to_user(
    role_id: RoleID, user: User, log_entry: UserLogEntry
) -> None:
    db_user_role = DbUserRole(user.id, role_id)
    db.session.add(db_user_role)

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()


def deassign_role_from_user(
    role_id: RoleID, user: User, *, initiator: User | None = None
) -> Result[RoleDeassignedFromUserEvent, str]:
    """Deassign the role from the user."""
    db_user_role = db.session.get(DbUserRole, (user.id, role_id))

    if db_user_role is None:
        return Err(f'Unknown role ID "{role_id}" and/or user ID "{user.id}"')

    event, log_entry = authz_domain_service.deassign_role_from_user(
        role_id, user, initiator=initiator
    )

    _persist_role_deassignment_from_user(db_user_role, log_entry)

    return Ok(event)


def _persist_role_deassignment_from_user(
    db_user_role: DbUserRole, log_entry: UserLogEntry
) -> None:
    db.session.delete(db_user_role)

    db_log_entry = user_log_service.to_db_entry(log_entry)
    db.session.add(db_log_entry)

    db.session.commit()


def deassign_all_roles_from_user(
    user: User, *, initiator: User | None = None, commit: bool = True
) -> None:
    """Deassign all roles from the user."""
    db.session.execute(delete(DbUserRole).where(DbUserRole.user_id == user.id))

    if commit:
        db.session.commit()


def _is_role_assigned_to_user(role_id: RoleID, user_id: UserID) -> bool:
    """Determine if the role is assigned to the user or not."""
    return (
        db.session.scalar(
            select(
                db.exists()
                .where(DbUserRole.role_id == role_id)
                .where(DbUserRole.user_id == user_id)
            )
        )
        or False
    )


def get_permission_ids_for_user(user_id: UserID) -> set[PermissionID]:
    """Return the IDs of all permissions the user has through the roles
    assigned to it.
    """
    db_role_permissions = db.session.scalars(
        select(DbRolePermission)
        .join(DbRole)
        .join(DbUserRole)
        .filter(DbUserRole.user_id == user_id)
    ).all()

    return {rp.permission_id for rp in db_role_permissions}


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
    role_ids = db.session.scalars(select(DbRole.id)).all()
    return set(role_ids)


def get_all_roles_with_permissions_and_users() -> list[
    tuple[Role, set[PermissionID], set[User]]
]:
    """Return all roles with titles, permission IDs, and assigned users."""
    db_roles = (
        db.session.scalars(
            select(DbRole).options(
                db.undefer(DbRole.title),
                db.joinedload(DbRole.user_roles).joinedload(DbUserRole.user),
            )
        )
        .unique()
        .all()
    )

    return [
        (
            _db_entity_to_role(db_role),
            {
                db_role_permission.permission_id
                for db_role_permission in db_role.role_permissions
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
    db_roles = (
        db.session.scalars(select(DbRole).options(db.undefer(DbRole.title)))
        .unique()
        .all()
    )

    role_ids_and_permission_ids = (
        db.session.execute(
            select(DbRolePermission.role_id, DbRolePermission.permission_id)
        )
        .tuples()
        .all()
    )

    return _index_permission_ids_by_role(role_ids_and_permission_ids, db_roles)


def get_permission_ids_by_role_for_user(
    user_id: UserID,
) -> dict[Role, frozenset[PermissionID]]:
    """Return permission IDs grouped by their respective roles for that
    user.

    Role titles are undeferred to avoid lots of additional queries.
    """
    db_roles = (
        db.session.scalars(
            select(DbRole)
            .options(db.undefer(DbRole.title))
            .join(DbUserRole)
            .filter(DbUserRole.user_id == user_id)
        )
        .unique()
        .all()
    )

    role_ids_and_permission_ids = (
        db.session.execute(
            select(DbRolePermission.role_id, DbRolePermission.permission_id)
            .join(DbRole)
            .join(DbUserRole)
            .filter(DbUserRole.user_id == user_id)
        )
        .tuples()
        .all()
    )

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
    permission_ids = db.session.scalars(
        select(DbRolePermission.permission_id).filter_by(role_id=role_id)
    ).all()

    return {PermissionID(permission_id) for permission_id in permission_ids}


def _db_entity_to_role(db_role: DbRole) -> Role:
    return Role(
        id=db_role.id,
        title=db_role.title,
    )
