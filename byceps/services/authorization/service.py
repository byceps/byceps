# -*- coding: utf-8 -*-

"""
byceps.services.authorization.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import defaultdict

from ...database import db

from .models import Permission, Role, RolePermission, UserRole


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
