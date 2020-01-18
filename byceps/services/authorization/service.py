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
    Permission,
    PermissionID,
    Role,
    RoleID,
    RolePermission,
    UserRole,
)


def create_permission(permission_id: PermissionID, title: str) -> Permission:
    """Create a permission."""
    permission = Permission(permission_id, title)

    db.session.add(permission)
    db.session.commit()

    return permission


def create_role(role_id: RoleID, title: str) -> Role:
    """Create a role."""
    role = Role(role_id, title)

    db.session.add(role)
    db.session.commit()

    return role


def find_role(role_id: RoleID) -> Optional[Role]:
    """Return the role with that id, or `None` if not found."""
    return Role.query.get(role_id)


def find_role_ids_for_user(user_id: UserID) -> Set[Role]:
    """Return the IDs of the roles assigned to the user."""
    roles = Role.query \
        .join(UserRole) \
        .filter(UserRole.user_id == user_id) \
        .all()

    return {r.id for r in roles}


def find_user_ids_for_role(role_id: RoleID) -> Set[UserID]:
    """Return the IDs of the users that have this role assigned."""
    rows = db.session \
        .query(UserRole.user_id) \
        .filter(UserRole.role_id == role_id) \
        .all()

    return {row[0] for row in rows}


def assign_permission_to_role(
    permission_id: PermissionID, role_id: RoleID
) -> None:
    """Assign the permission to the role."""
    role_permission = RolePermission(role_id, permission_id)

    db.session.add(role_permission)
    db.session.commit()


def deassign_permission_from_role(
    permission_id: PermissionID, role_id: RoleID
) -> None:
    """Dessign the permission from the role."""
    role_permission = RolePermission.query.get((role_id, permission_id))

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

    user_role = UserRole(user_id, role_id)
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
    user_role = UserRole.query.get((user_id, role_id))

    if user_role is None:
        raise ValueError('Unknown user ID and/or role ID.')

    db.session.delete(user_role)

    event_data = {'role_id': str(role_id)}
    if initiator_id is not None:
        event_data['initiator_id'] = str(initiator_id)
    event = user_event_service.build_event('role-deassigned', user_id, event_data)
    db.session.add(event)

    db.session.commit()


def deassign_all_roles_from_user(
    user_id: UserID, initiator_id: Optional[UserID] = None, commit=True
) -> None:
    """Deassign all roles from the user."""
    table = UserRole.__table__
    delete_query = table.delete() \
        .where(table.c.user_id == user_id)
    db.session.execute(delete_query)

    if commit:
        db.session.commit()


def _is_role_assigned_to_user(role_id: RoleID, user_id: UserID) -> bool:
    """Determine if the role is assigned to the user or not."""
    subquery = UserRole.query \
        .filter_by(role_id=role_id) \
        .filter_by(user_id=user_id) \
        .exists()

    return db.session.query(subquery).scalar()


def get_permission_ids_for_user(user_id: UserID) -> Set[PermissionID]:
    """Return the IDs of all permissions the user has through the roles
    assigned to it.
    """
    role_permissions = RolePermission.query \
        .join(Role) \
        .join(UserRole) \
        .filter_by(user_id=user_id) \
        .all()

    return {rp.permission_id for rp in role_permissions}


def get_all_permissions_with_titles() -> Sequence[Permission]:
    """Return all permissions, with titles."""
    return Permission.query \
        .options(
            db.undefer('title'),
            db.joinedload('role_permissions')
        ) \
        .all()


def get_all_roles_with_titles() -> Sequence[Role]:
    """Return all roles, with titles."""
    return Role.query \
        .options(
            db.undefer('title'),
            db.joinedload('user_roles').joinedload('user')
        ) \
        .all()


def get_permissions_by_roles_with_titles() -> Dict[Role, Set[Permission]]:
    """Return all roles with their assigned permissions.

    Titles are undeferred to avoid lots of additional queries.
    """
    roles = Role.query \
        .options(
            db.undefer('title'),
        ) \
        .all()

    permissions = Permission.query \
        .options(
            db.undefer('title'),
            db.joinedload('role_permissions').joinedload('role')
        ) \
        .all()

    permissions_by_role: Dict[Role, Set[Permission]] = {r: set() for r in roles}

    for permission in permissions:
        for role in permission.roles:
            if role in permissions_by_role:
                permissions_by_role[role].add(permission)

    return permissions_by_role


def get_permissions_by_roles_for_user_with_titles(
    user_id: UserID
) -> Dict[Role, Set[Permission]]:
    """Return permissions grouped by their respective roles for that user.

    Titles are undeferred to avoid lots of additional queries.
    """
    roles = Role.query \
        .options(
            db.undefer('title'),
        ) \
        .join(UserRole) \
        .filter(UserRole.user_id == user_id) \
        .all()

    role_ids = {r.id for r in roles}

    if role_ids:
        permissions = Permission.query \
            .options(
                db.undefer('title'),
                db.joinedload('role_permissions').joinedload('role')
            ) \
            .join(RolePermission) \
            .join(Role) \
            .filter(Role.id.in_(role_ids)) \
            .all()
    else:
        permissions = []

    return _index_permissions_by_role(permissions, roles)


def _index_permissions_by_role(
    permissions: List[Permission], roles: List[Role]
) -> Dict[Role, Set[Permission]]:
    permissions_by_role: Dict[Role, Set[Permission]] = {r: set() for r in roles}

    for permission in permissions:
        for role in permission.roles:
            if role in permissions_by_role:
                permissions_by_role[role].add(permission)

    return permissions_by_role


def get_permissions_with_title_for_role(
    role_id: RoleID
) -> Sequence[Permission]:
    """Return the permissions assigned to the role."""
    return Permission.query \
        .options(
            db.undefer('title')
        ) \
        .join(RolePermission) \
        .filter(RolePermission.role_id == role_id) \
        .all()
