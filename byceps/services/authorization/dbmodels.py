"""
byceps.services.authorization.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.ext.associationproxy import association_proxy

from byceps.database import db
from byceps.services.user.dbmodels.user import DbUser
from byceps.typing import UserID
from byceps.util.instances import ReprBuilder

from .models import PermissionID, RoleID


class DbRole(db.Model):
    """A role.

    Combines one or more permissions.

    Can be assigned to a user.
    """

    __tablename__ = 'authz_roles'

    id = db.Column(db.UnicodeText, primary_key=True)
    title = db.deferred(db.Column(db.UnicodeText, unique=True, nullable=False))

    users = association_proxy('user_roles', 'user')

    def __init__(self, role_id: RoleID, title: str) -> None:
        self.id = role_id
        self.title = title

    def __repr__(self) -> str:
        return ReprBuilder(self).add_with_lookup('id').build()


class DbRolePermission(db.Model):
    """The assignment of a permission to a role."""

    __tablename__ = 'authz_role_permissions'

    role_id = db.Column(
        db.UnicodeText, db.ForeignKey('authz_roles.id'), primary_key=True
    )
    role = db.relationship(
        DbRole,
        backref=db.backref(
            'role_permissions', collection_class=set, lazy='joined'
        ),
        collection_class=set,
    )
    permission_id = db.Column(db.UnicodeText, primary_key=True)

    def __init__(self, role_id: RoleID, permission_id: PermissionID) -> None:
        self.role_id = role_id
        self.permission_id = permission_id

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('role_id')
            .add_with_lookup('permission_id')
            .build()
        )


class DbUserRole(db.Model):
    """The assignment of a role to a user."""

    __tablename__ = 'authz_user_roles'

    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), primary_key=True)
    user = db.relationship(
        DbUser,
        backref=db.backref('user_roles', collection_class=set),
        collection_class=set,
    )
    role_id = db.Column(
        db.UnicodeText, db.ForeignKey('authz_roles.id'), primary_key=True
    )
    role = db.relationship(
        DbRole,
        backref=db.backref('user_roles', collection_class=set),
        collection_class=set,
        lazy='joined',
    )

    def __init__(self, user_id: UserID, role_id: RoleID) -> None:
        self.user_id = user_id
        self.role_id = role_id

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('user')
            .add_with_lookup('role')
            .build()
        )
