"""
byceps.services.authorization.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType

from sqlalchemy.ext.associationproxy import association_proxy

from ...database import db
from ...typing import UserID
from ...util.instances import ReprBuilder

from ..user.models.user import User


PermissionID = NewType('PermissionID', str)

RoleID = NewType('RoleID', str)


class Permission(db.Model):
    """A permission for a specific task.

    Can be assigned to one or more roles.
    """

    __tablename__ = 'authz_permissions'

    id = db.Column(db.UnicodeText, primary_key=True)
    title = db.deferred(db.Column(db.UnicodeText, unique=True, nullable=False))

    roles = association_proxy('role_permissions', 'role')

    def __init__(self, permission_id: PermissionID, title: str) -> None:
        self.id = permission_id
        self.title = title

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()


class Role(db.Model):
    """A role.

    Combines one or more permissions.

    Can be assigned to a user.
    """

    __tablename__ = 'authz_roles'

    id = db.Column(db.UnicodeText, primary_key=True)
    title = db.deferred(db.Column(db.UnicodeText, unique=True, nullable=False))

    permissions = association_proxy('role_permissions', 'permission')
    users = association_proxy('user_roles', 'user')

    def __init__(self, role_id: RoleID, title: str) -> None:
        self.id = role_id
        self.title = title

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .build()


class RolePermission(db.Model):
    """The assignment of a permission to a role."""

    __tablename__ = 'authz_role_permissions'

    role_id = db.Column(db.UnicodeText, db.ForeignKey('authz_roles.id'), primary_key=True)
    role = db.relationship(Role,
                           backref=db.backref('role_permissions', collection_class=set, lazy='joined'),
                           collection_class=set)
    permission_id = db.Column(db.UnicodeText, db.ForeignKey('authz_permissions.id'), primary_key=True)
    permission = db.relationship(Permission, backref='role_permissions', collection_class=set, lazy='joined')

    def __init__(self, role_id: RoleID, permission_id: PermissionID) -> None:
        self.role_id = role_id
        self.permission_id = permission_id

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('role') \
            .add_with_lookup('permission') \
            .build()


class UserRole(db.Model):
    """The assignment of a role to a user."""

    __tablename__ = 'authz_user_roles'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(User,
                           backref=db.backref('user_roles', collection_class=set),
                           collection_class=set)
    role_id = db.Column(db.UnicodeText, db.ForeignKey('authz_roles.id'), primary_key=True)
    role = db.relationship(Role,
                           backref=db.backref('user_roles', collection_class=set),
                           collection_class=set,
                           lazy='joined')

    def __init__(self, user_id: UserID, role_id: RoleID) -> None:
        self.user_id = user_id
        self.role_id = role_id

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('user') \
            .add_with_lookup('role') \
            .build()
