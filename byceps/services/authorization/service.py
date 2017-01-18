# -*- coding: utf-8 -*-

"""
byceps.services.authorization.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2017 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import defaultdict

from ...database import db

from .models import Permission, Role, RolePermission, UserRole


def create_permission(permission_id, title):
    """Create a permission."""
    permission = Permission(permission_id, title)

    db.session.add(permission)
    db.session.commit()

    return permission


def create_role(role_id, title):
    """Create a role."""
    role = Role(role_id, title)

    db.session.add(role)
    db.session.commit()

    return role


def assign_permission_to_role(permission, role):
    """Assign the permission to the role."""
    role_permission = RolePermission(permission)
    role_permission.role = role

    db.session.add(role_permission)
    db.session.commit()


def assign_role_to_user(role, user):
    """Assign the role to the user."""
    user_role = UserRole(role)
    user_role.user = user

    db.session.add(user_role)
    db.session.commit()


def find_role(role_id):
    """Return the role with that id, or `None` if not found."""
    return Role.query.get(role_id)


def get_permission_ids_for_user(user_id):
    """Return the IDs of all permissions the user has through the roles
    assigned to it.
    """
    role_permissions = RolePermission.query \
        .join(Role) \
        .join(UserRole) \
        .filter_by(user_id=user_id) \
        .all()

    return frozenset(rp.permission_id for rp in role_permissions)


def get_permissions_with_titles():
    """Return all permissions, with titles."""
    return Permission.query \
        .options(
            db.undefer('title'),
            db.joinedload('role_permissions')
        ) \
        .all()


def get_roles_with_titles():
    """Return all roles, with titles."""
    return Role.query \
        .options(
            db.undefer('title'),
            db.joinedload('user_roles').joinedload('user')
        ) \
        .all()


def get_permissions_by_roles_for_user_with_titles(user):
    """Return permissions grouped by their respective roles for that user.

    Titles are undeferred to avoid lots of additional queries.
    """
    permissions = Permission.query \
        .options(
            db.undefer('title'),
            db.joinedload('role_permissions').joinedload('role').undefer('title')
        ) \
        .join(RolePermission) \
        .join(Role) \
        .join(UserRole) \
        .filter(UserRole.user == user) \
        .all()

    permissions_by_role = defaultdict(set)

    for permission in permissions:
        for role in permission.roles:
            permissions_by_role[role].add(permission)

    return permissions_by_role
