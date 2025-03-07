"""
byceps.services.user_group.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2025 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.party.models import PartyID
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.user import UserID
from byceps.util.instances import ReprBuilder


class DbUserGroup(db.Model):
    """A self-organized group of users."""

    __tablename__ = 'user_groups'
    __table_args__ = (db.UniqueConstraint('party_id', 'title'),)

    id: Mapped[UUID] = mapped_column(db.Uuid, primary_key=True)
    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True
    )
    created_at: Mapped[datetime]
    creator_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), unique=True
    )
    creator: Mapped[DbUser] = relationship(DbUser)
    title: Mapped[str] = mapped_column(db.UnicodeText, unique=True)
    description: Mapped[str | None] = mapped_column(db.UnicodeText)

    members = association_proxy('memberships', 'user')

    def __init__(
        self,
        group_id: UUID,
        party_id: PartyID,
        created_at: datetime,
        creator_id: UserID,
        title: str,
        description: str | None = None,
    ) -> None:
        self.id = group_id
        self.party_id = party_id
        self.created_at = created_at
        self.creator_id = creator_id
        self.title = title
        self.description = description

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('party_id')
            .add_with_lookup('title')
            .build()
        )


class DbUserGroupMembership(db.Model):
    """The assignment of a user to a user group.

    A user must not be a member of more than one group per party.
    """

    __tablename__ = 'user_group_memberships'

    id: Mapped[UUID] = mapped_column(db.Uuid, primary_key=True)
    group_id: Mapped[UUID] = mapped_column(
        db.Uuid, db.ForeignKey('user_groups.id')
    )
    group: Mapped[DbUserGroup] = relationship(
        DbUserGroup, collection_class=set, backref='memberships'
    )
    user_id: Mapped[UserID] = mapped_column(db.Uuid, db.ForeignKey('users.id'))
    user: Mapped[DbUser] = relationship(DbUser, backref='group_membership')
    created_at: Mapped[datetime]

    def __init__(
        self,
        membership_id: UUID,
        group_id: UUID,
        user_id: UserID,
        created_at: datetime,
    ) -> None:
        self.id = membership_id
        self.group_id = group_id
        self.user_id = user_id
        self.created_at = created_at

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add_with_lookup('group')
            .add_with_lookup('user')
            .build()
        )
