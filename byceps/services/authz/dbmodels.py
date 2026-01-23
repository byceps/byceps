"""
byceps.services.authz.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.user.dbmodels import DbUser
from byceps.services.user.models.user import UserID

from .models import PermissionID, RoleID


class DbRole(db.Model):
    """A role.

    Combines one or more permissions.

    Can be assigned to a user.
    """

    __tablename__ = 'authz_roles'

    id: Mapped[RoleID] = mapped_column(db.UnicodeText, primary_key=True)
    title: Mapped[str] = db.deferred(
        mapped_column(db.UnicodeText, unique=True, nullable=False)
    )

    users = association_proxy('user_roles', 'user')

    def __init__(self, role_id: RoleID, title: str) -> None:
        self.id = role_id
        self.title = title


class DbRolePermission(db.Model):
    """The assignment of a permission to a role."""

    __tablename__ = 'authz_role_permissions'

    role_id: Mapped[RoleID] = mapped_column(
        db.UnicodeText, db.ForeignKey('authz_roles.id'), primary_key=True
    )
    role: Mapped[DbRole] = relationship(
        DbRole,
        backref=db.backref(
            'role_permissions', collection_class=set, lazy='joined'
        ),
        collection_class=set,
    )
    permission_id: Mapped[PermissionID] = mapped_column(
        db.UnicodeText, primary_key=True
    )

    def __init__(self, role_id: RoleID, permission_id: PermissionID) -> None:
        self.role_id = role_id
        self.permission_id = permission_id


class DbUserRole(db.Model):
    """The assignment of a role to a user."""

    __tablename__ = 'authz_user_roles'

    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), primary_key=True
    )
    user: Mapped[DbUser] = relationship(
        DbUser,
        backref=db.backref('user_roles', collection_class=set),
        collection_class=set,
    )
    role_id: Mapped[RoleID] = mapped_column(
        db.UnicodeText, db.ForeignKey('authz_roles.id'), primary_key=True
    )
    role: Mapped[DbRole] = relationship(
        DbRole,
        backref=db.backref('user_roles', collection_class=set),
        collection_class=set,
        lazy='joined',
    )

    def __init__(self, user_id: UserID, role_id: RoleID) -> None:
        self.user_id = user_id
        self.role_id = role_id
