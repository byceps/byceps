"""
byceps.services.user_group.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2022 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.associationproxy import association_proxy

from ...database import db, generate_uuid
from ...typing import PartyID, UserID
from ...util.instances import ReprBuilder

from ..user.dbmodels.user import DbUser


class DbUserGroup(db.Model):
    """A self-organized group of users."""

    __tablename__ = 'user_groups'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'title'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.UnicodeText, db.ForeignKey('parties.id'), index=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    creator_id = db.Column(db.Uuid, db.ForeignKey('users.id'), unique=True, nullable=False)
    creator = db.relationship(DbUser)
    title = db.Column(db.UnicodeText, unique=True, nullable=False)
    description = db.Column(db.UnicodeText, nullable=True)

    members = association_proxy('memberships', 'user')

    def __init__(
        self,
        party_id: PartyID,
        creator_id: UserID,
        title: str,
        description: Optional[str] = None,
    ) -> None:
        self.party_id = party_id
        self.creator_id = creator_id
        self.title = title
        self.description = description

    @property
    def member_count(self) -> int:
        return len(self.members)

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('party_id') \
            .add_with_lookup('title') \
            .build()


class DbMembership(db.Model):
    """The assignment of a user to a user group.

    A user must not be a member of more than one group per party.
    """

    __tablename__ = 'user_group_memberships'

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    group_id = db.Column(db.Uuid, db.ForeignKey('user_groups.id'))
    group = db.relationship(DbUserGroup, collection_class=set, backref='memberships')
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'))
    user = db.relationship(DbUser, backref='group_membership')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('group') \
            .add_with_lookup('user') \
            .build()
