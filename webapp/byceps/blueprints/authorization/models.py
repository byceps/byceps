# -*- coding: utf-8 -*-

"""
byceps.blueprints.authorization.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2014 Jochen Kupperschmidt
"""

from sqlalchemy.ext.associationproxy import association_proxy

from ...database import db
from ...util.instances import ReprBuilder

from ..user.models import User

from .registry import permission_registry


class Permission(db.Model):
    """A permission for a specific task.

    Can be assigned to one or more roles.
    """
    __tablename__ = 'permissions'

    id = db.Column(db.Unicode(40), primary_key=True)

    @property
    def enum_member(self):
        return permission_registry.get_enum_member(self)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()


class Role(db.Model):
    """A role.

    Combines one or more permissions.

    Can be assigned to a user.
    """
    __tablename__ = 'roles'

    id = db.Column(db.Unicode(40), primary_key=True)

    permissions = association_proxy('role_permissions', 'permission')

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()


class RolePermission(db.Model):
    """The assignment of a permission to a role."""
    __tablename__ = 'role_permissions'

    role_id = db.Column(db.Unicode(40), db.ForeignKey('roles.id'), primary_key=True)
    role = db.relationship(Role, backref='role_permissions', collection_class=set)
    permission_id = db.Column(db.Unicode(40), db.ForeignKey('permissions.id'), primary_key=True)
    permission = db.relationship(Permission, collection_class=set)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('role') \
            .add_with_lookup('permission') \
            .build()


class UserRole(db.Model):
    """The assignment of a role to a user."""
    __tablename__ = 'user_roles'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(User, backref='user_roles', collection_class=set)
    role_id = db.Column(db.Unicode(40), db.ForeignKey('roles.id'), primary_key=True)
    role = db.relationship(Role, collection_class=set)

    def __repr__(self):
        return ReprBuilder(self) \
            .add_with_lookup('user') \
            .add_with_lookup('role') \
            .build()
