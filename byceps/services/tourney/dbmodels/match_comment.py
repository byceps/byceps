"""
byceps.services.tourney.dbmodels.match_comment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Copyright: 2014-2026 Jochen Kupperschmidt
:License: Revised BSD (see `LICENSE` file for details)
"""

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship

from byceps.database import db
from byceps.services.tourney.models import MatchCommentID, MatchID
from byceps.services.user.dbmodels import DbUser
from byceps.services.user.models import UserID

from .match import DbMatch


class DbMatchComment(db.Model):
    """An immutable comment on a match by one of the opponents."""

    __tablename__ = 'tourney_match_comments'

    id: Mapped[MatchCommentID] = mapped_column(db.Uuid, primary_key=True)
    match_id: Mapped[MatchID] = mapped_column(
        db.Uuid, db.ForeignKey('tourney_matches.id'), index=True
    )
    match: Mapped[DbMatch] = relationship()
    created_at: Mapped[datetime]
    created_by_id: Mapped[UserID] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    created_by: Mapped[DbUser] = relationship(foreign_keys=[created_by_id])
    body: Mapped[str] = mapped_column(db.UnicodeText)
    last_edited_at: Mapped[datetime | None]
    last_edited_by_id: Mapped[UserID | None] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    last_edited_by: Mapped[DbUser | None] = relationship(
        foreign_keys=[last_edited_by_id]
    )
    hidden: Mapped[bool] = mapped_column(default=False)
    hidden_at: Mapped[datetime | None]
    hidden_by_id: Mapped[UserID | None] = mapped_column(
        db.Uuid, db.ForeignKey('users.id')
    )
    hidden_by: Mapped[DbUser | None] = relationship(foreign_keys=[hidden_by_id])

    def __init__(
        self,
        comment_id: MatchCommentID,
        match_id: MatchID,
        created_at: datetime,
        creator_id: UserID,
        body: str,
    ) -> None:
        self.id = comment_id
        self.match_id = match_id
        self.created_at = created_at
        self.created_by_id = creator_id
        self.body = body
