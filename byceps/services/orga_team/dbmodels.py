"""
byceps.services.orga_team.dbmodels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2023 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.party.dbmodels import DbParty
from byceps.services.party.models import PartyID
from byceps.services.user.dbmodels.user import DbUser
from byceps.services.user.models.user import UserID
from byceps.util.instances import ReprBuilder
from byceps.util.uuid import generate_uuid7

from .models import MembershipID, OrgaTeamID


class DbOrgaTeam(db.Model):
    """A group of organizers for a single party."""

    __tablename__ = 'orga_teams'
    __table_args__ = (db.UniqueConstraint('party_id', 'title'),)

    id: Mapped[OrgaTeamID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    party_id: Mapped[PartyID] = mapped_column(
        db.UnicodeText, db.ForeignKey('parties.id'), index=True
    )
    party: Mapped[DbParty] = relationship(DbParty)
    title: Mapped[str] = mapped_column(db.UnicodeText)

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
    __table_args__ = (db.UniqueConstraint('orga_team_id', 'user_id'),)

    id: Mapped[MembershipID] = mapped_column(
        db.Uuid, default=generate_uuid7, primary_key=True
    )
    orga_team_id: Mapped[OrgaTeamID] = mapped_column(
        db.Uuid, db.ForeignKey('orga_teams.id'), index=True
    )
    orga_team: Mapped[DbOrgaTeam] = relationship(
        DbOrgaTeam, collection_class=set, backref='memberships'
    )
    user_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id'), index=True
    )
    user: Mapped[DbUser] = relationship(
        DbUser, collection_class=set, backref='orga_team_memberships'
    )
    duties: Mapped[str | None] = mapped_column(db.UnicodeText)

    def __init__(
        self,
        orga_team_id: OrgaTeamID,
        user_id: UserID,
        *,
        duties: str | None = None,
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
