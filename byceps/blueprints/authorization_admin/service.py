# -*- coding: utf-8 -*-

"""
byceps.blueprints.authorization.service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from collections import defaultdict

from ...database import db

from ..authorization.models import Permission, Role, RolePermission, UserRole


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
