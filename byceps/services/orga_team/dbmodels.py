"""
byceps.services.orga_team.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from typing import Optional

from ...database import db, generate_uuid
from ...typing import PartyID, UserID
from ...util.instances import ReprBuilder

from ..party.dbmodels.party import DbParty
from ..user.dbmodels.user import DbUser

from .transfer.models import OrgaTeamID


class DbOrgaTeam(db.Model):
    """A group of organizers for a single party."""

    __tablename__ = 'orga_teams'
    __table_args__ = (
        db.UniqueConstraint('party_id', 'title'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    party_id = db.Column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True, nullable=False
    )
    party = db.relationship(DbParty)
    title = db.Column(db.UnicodeText, nullable=False)

    def __init__(self, party_id: PartyID, title: str) -> None:
        self.party_id = party_id
        self.title = title

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add_with_lookup('party_id')
            .add_with_lookup('title')
            .build()
        )


class DbMembership(db.Model):
    """The assignment of a user to an organizer team."""

    __tablename__ = 'orga_team_memberships'
    __table_args__ = (
        db.UniqueConstraint('orga_team_id', 'user_id'),
    )

    id = db.Column(db.Uuid, default=generate_uuid, primary_key=True)
    orga_team_id = db.Column(
        db.Uuid, db.ForeignKey('orga_teams.id'), index=True, nullable=False
    )
    orga_team = db.relationship(
        DbOrgaTeam, collection_class=set, backref='memberships'
    )
    user_id = db.Column(
        db.Uuid, db.ForeignKey('users.id'), index=True, nullable=False
    )
    user = db.relationship(
        DbUser, collection_class=set, backref='orga_team_memberships'
    )
    duties = db.Column(db.UnicodeText, nullable=True)

    def __init__(
        self,
        orga_team_id: OrgaTeamID,
        user_id: UserID,
        *,
        duties: Optional[str] = None,
    ) -> None:
        self.orga_team_id = orga_team_id
        self.user_id = user_id
        self.duties = duties

    def __repr__(self) -> str:
        return (
            ReprBuilder(self)
            .add_with_lookup('id')
            .add_with_lookup('orga_team')
            .add_with_lookup('user')
            .build()
        )
