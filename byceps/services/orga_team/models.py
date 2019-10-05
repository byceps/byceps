"""
byceps.services.orga_team.models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
"""

from typing import NewType
from uuid import UUID

from ...database import BaseQuery, db, generate_uuid
from ...typing import PartyID, UserID
from ...util.instances import ReprBuilder

from ..party.models.party import Party
from ..user.models.user import User


OrgaTeamID = NewType('OrgaTeamID', UUID)


class OrgaTeam(db.Model):
    """A group of organizers for a single party."""

    __tablename__ = 'orga_teams'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'title'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(db.UnicodeText, db.ForeignKey('parties.id'), index=True, nullable=False)
    party = db.relationship(Party)
    title = db.Column(db.UnicodeText, nullable=False)

    def __init__(self, party_id: PartyID, title: str) -> None:
        self.party_id = party_id
        self.title = title

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('party_id') \
            .add_with_lookup('title') \
            .add_custom('{:d} members'.format(len(self.memberships))) \
            .build()


class MembershipQuery(BaseQuery):

    def for_party(self, party_id: PartyID) -> BaseQuery:
        return self.join(OrgaTeam).filter_by(party_id=party_id)


MembershipID = NewType('MembershipID', UUID)


class Membership(db.Model):
    """The assignment of a user to an organizer team."""

    __tablename__ = 'orga_team_memberships'
    __table_args__ = (
        db.UniqueConstraint('orga_team_id', 'user_id'),
    )
    query_class = MembershipQuery

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    orga_team_id = db.Column(db.Uuid, db.ForeignKey('orga_teams.id'), index=True, nullable=False)
    orga_team = db.relationship(OrgaTeam, collection_class=set, backref='memberships')
    user_id = db.Column(db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False)
    user = db.relationship(User, collection_class=set, backref='orga_team_memberships')
    duties = db.Column(db.UnicodeText)

    def __init__(self, orga_team_id: OrgaTeamID, user_id: UserID) -> None:
        self.orga_team_id = orga_team_id
        self.user_id = user_id

    def __repr__(self) -> str:
        return ReprBuilder(self) \
            .add_with_lookup('id') \
            .add_with_lookup('orga_team') \
            .add_with_lookup('user') \
            .build()
