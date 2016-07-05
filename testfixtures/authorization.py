# -*- coding: utf-8 -*-

"""
testfixtures.authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2016 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from byceps.blueprints.authorization.models import Permission, Role


def create_permission(id, title=None):
    return Permission(id, title)


def create_permission_from_enum_member(permission_enum_member):
    return Permission.from_enum_member(permission_enum_member)


def create_role(id, title=None):
    if title is None:
        title = id

    return Role(id, title)
