"""
byceps.services.authorization.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2020 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import Dict, List, Optional, Sequence, Set

from ...database import db
from ...typing import UserID

from ..user import event_service as user_event_service

from .models import (
    Permission as DbPermission,
    Role as DbRole,
    RolePermission as DbRolePermission,
    UserRole as DbUserRole,
)
from .transfer.models import Permission, PermissionID, Role, RoleID


def create_permission(permission_id: PermissionID, title: str) -> Permission:
    """Create a permission."""
    permission = DbPermission(permission_id, title)

    db.session.add(permission)
    db.session.commit()

    return _db_entity_to_permission(permission)


def delete_permission(permission_id: PermissionID) -> None:
    """Delete a permission."""
    db.session.query(DbPermission) \
        .filter_by(id=permission_id) \
        .delete()

    db.session.commit()


def create_role(role_id: RoleID, title: str) -> Role:
    """Create a role."""
    role = DbRole(role_id, title)

    db.session.add(role)
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
    role = DbRole.query.get(role_id)

    if role is None:
        return None

    return _db_entity_to_role(role)


def find_role_ids_for_user(user_id: UserID) -> Set[RoleID]:
    """Return the IDs of the roles assigned to the user."""
    roles = DbRole.query \
        .join(DbUserRole) \
        .filter(DbUserRole.user_id == user_id) \
        .all()

    return {r.id for r in roles}


def find_user_ids_for_role(role_id: RoleID) -> Set[UserID]:
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
    role_permission = DbRolePermission.query.get((role_id, permission_id))

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

    event_data = {'role_id': str(role_id)}
    if initiator_id is not None:
        event_data['initiator_id'] = str(initiator_id)
    event = user_event_service.build_event('role-assigned', user_id, event_data)
    db.session.add(event)

    db.session.commit()


def deassign_role_from_user(
    role_id: RoleID, user_id: UserID, initiator_id: Optional[UserID] = None
) -> None:
    """Deassign the role from the user."""
    user_role = DbUserRole.query.get((user_id, role_id))

    if user_role is None:
        raise ValueError('Unknown user ID and/or role ID.')

    db.session.delete(user_role)

    event_data = {'role_id': str(role_id)}
    if initiator_id is not None:
        event_data['initiator_id'] = str(initiator_id)
    event = user_event_service.build_event(
        'role-deassigned', user_id, event_data
    )
    db.session.add(event)

    db.session.commit()


def deassign_all_roles_from_user(
    user_id: UserID, initiator_id: Optional[UserID] = None, commit=True
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
    subquery = DbUserRole.query \
        .filter_by(role_id=role_id) \
        .filter_by(user_id=user_id) \
        .exists()

    return db.session.query(subquery).scalar()


def get_permission_ids_for_user(user_id: UserID) -> Set[PermissionID]:
    """Return the IDs of all permissions the user has through the roles
    assigned to it.
    """
    role_permissions = DbRolePermission.query \
        .join(DbRole) \
        .join(DbUserRole) \
        .filter_by(user_id=user_id) \
        .all()

    return {rp.permission_id for rp in role_permissions}


def get_all_permissions_with_titles() -> Sequence[Permission]:
    """Return all permissions, with titles."""
    permissions = DbPermission.query \
        .options(
            db.undefer('title'),
            db.joinedload('role_permissions')
        ) \
        .all()

    return [_db_entity_to_permission(permission) for permission in permissions]


def get_all_roles_with_titles() -> Sequence[DbRole]:
    """Return all roles, with titles."""
    return DbRole.query \
        .options(
            db.undefer('title'),
            db.joinedload('user_roles').joinedload('user')
        ) \
        .all()


def get_permissions_by_roles_with_titles() -> Dict[Role, Set[Permission]]:
    """Return all roles with their assigned permissions.

    Titles are undeferred to avoid lots of additional queries.
    """
    roles = DbRole.query \
        .options(
            db.undefer('title'),
        ) \
        .all()

    permissions = DbPermission.query \
        .options(
            db.undefer('title'),
            db.joinedload('role_permissions').joinedload('role')
        ) \
        .all()

    return _index_permissions_by_role(permissions, roles)


def get_permissions_by_roles_for_user_with_titles(
    user_id: UserID,
) -> Dict[Role, Set[Permission]]:
    """Return permissions grouped by their respective roles for that user.

    Titles are undeferred to avoid lots of additional queries.
    """
    roles = DbRole.query \
        .options(
            db.undefer('title'),
        ) \
        .join(DbUserRole) \
        .filter(DbUserRole.user_id == user_id) \
        .all()

    role_ids = {r.id for r in roles}

    if role_ids:
        permissions = DbPermission.query \
            .options(
                db.undefer('title'),
                db.joinedload('role_permissions').joinedload('role')
            ) \
            .join(DbRolePermission) \
            .join(DbRole) \
            .filter(DbRole.id.in_(role_ids)) \
            .all()
    else:
        permissions = []

    return _index_permissions_by_role(permissions, roles)


def _index_permissions_by_role(
    permissions: List[DbPermission], roles: List[DbRole]
) -> Dict[Role, Set[Permission]]:
    permissions_by_role: Dict[DbRole, Set[DbPermission]] = {
        role: set() for role in roles
    }

    for permission in permissions:
        for role in permission.roles:
            if role in permissions_by_role:
                permissions_by_role[role].add(permission)

    # Convert database entities to transfer objects.
    return {
        _db_entity_to_role(role): {
            _db_entity_to_permission(permission) for permission in permissions
        }
        for role, permissions in permissions_by_role.items()
    }


def get_permissions_with_title_for_role(
    role_id: RoleID,
) -> Sequence[Permission]:
    """Return the permissions assigned to the role."""
    permissions = DbPermission.query \
        .options(
            db.undefer('title')
        ) \
        .join(DbRolePermission) \
        .filter(DbRolePermission.role_id == role_id) \
        .all()

    return [_db_entity_to_permission(permission) for permission in permissions]


def _db_entity_to_permission(permission: DbPermission) -> Permission:
    return Permission(
        permission.id,
        permission.title,
    )


def _db_entity_to_role(role: DbRole) -> Role:
    return Role(
        role.id,
        role.title,
    )
